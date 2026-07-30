import os
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class Neo4jGraphDB:
    """
    Dedicated Medical Knowledge Graph Engine using Neo4j and Cypher Query Language
    """
    _driver = None

    @classmethod
    def get_driver(cls):
        if cls._driver is None:
            try:
                from neo4j import GraphDatabase
                uri = os.environ.get('NEO4J_URI', 'bolt://neo4j:7687')
                user = os.environ.get('NEO4J_USER', 'neo4j')
                password = os.environ.get('NEO4J_PASSWORD', 'healthcare_neo4j_2026')
                
                cls._driver = GraphDatabase.driver(uri, auth=(user, password))
                logger.info(f"[Neo4j GraphDB] Connected to Neo4j at {uri}")
            except Exception as e:
                logger.warning(f"[Neo4j GraphDB] Connection failed: {e}. Graph features will fallback gracefully.")
                return None
        return cls._driver

    @classmethod
    def close(cls):
        if cls._driver is not None:
            cls._driver.close()
            cls._driver = None

    @classmethod
    def run_query(cls, cypher_query, parameters=None):
        driver = cls.get_driver()
        if not driver:
            return None
        try:
            with driver.session() as session:
                result = session.run(cypher_query, parameters or {})
                return [record.data() for record in result]
        except Exception as e:
            logger.error(f"[Neo4j Query Error] {e}")
            return None

    @classmethod
    def check_drug_interaction(cls, drug_a_name, drug_b_name):
        """
        Duyệt đồ thị tìm tương tác giữa 2 thuốc
        """
        query = """
        MATCH (d1:Drug)-[r:INTERACTS_WITH]-(d2:Drug)
        WHERE toLower(d1.name) CONTAINS toLower($name_a) AND toLower(d2.name) CONTAINS toLower($name_b)
        RETURN d1.name AS drug_a, d2.name AS drug_b, 
               r.severity AS severity, r.mechanism AS mechanism, 
               r.clinical_effect AS clinical_effect, r.recommendation AS recommendation
        LIMIT 5
        """
        return cls.run_query(query, {'name_a': drug_a_name, 'name_b': drug_b_name})

    @classmethod
    def find_differential_diagnosis(cls, symptom_keywords):
        """
        Duyệt đồ thị Symptom ➔ Disease để đưa ra chẩn đoán phân biệt
        """
        query = """
        MATCH (s:Symptom)-[r:INDICATES]->(d:Disease)
        WHERE any(kw IN $symptoms WHERE toLower(s.name) CONTAINS toLower(kw))
        RETURN d.name AS disease_name, d.icd_code AS icd_code, d.description AS description,
               collect(s.name) AS matched_symptoms, count(s) AS score
        ORDER BY score DESC
        LIMIT 5
        """
        keywords = symptom_keywords if isinstance(symptom_keywords, list) else [symptom_keywords]
        return cls.run_query(query, {'symptoms': keywords})

    @classmethod
    def check_allergy_cross_reaction(cls, allergen_name, drug_name):
        """
        Kiểm tra dị ứng chéo giữa dị ứng bệnh nhân và thuốc kê đơn trên đồ thị
        """
        query = """
        MATCH (d:Drug)-[r:HAS_ALLERGEN]->(a:Allergen)
        WHERE toLower(d.name) CONTAINS toLower($drug) AND toLower(a.name) CONTAINS toLower($allergen)
        RETURN d.name AS drug_name, a.name AS allergen_name, r.risk_level AS risk_level, r.note AS note
        """
        return cls.run_query(query, {'drug': drug_name, 'allergen': allergen_name})

    @classmethod
    def get_treatment_protocol(cls, disease_name):
        """
        Tra cứu phác đồ điều trị Disease ➔ Drug trên đồ thị
        """
        query = """
        MATCH (d:Disease)-[r:TREATED_BY]->(dr:Drug)
        WHERE toLower(d.name) CONTAINS toLower($disease)
        RETURN d.name AS disease, dr.name AS drug, r.line_of_treatment AS line, r.notes AS notes
        """
        return cls.run_query(query, {'disease': disease_name})

    @classmethod
    def health_check(cls):
        """
        Kiểm tra trạng thái kết nối và số lượng Node / Relationship trong Neo4j
        """
        query = """
        MATCH (n)
        OPTIONAL MATCH (n)-[r]->()
        RETURN count(DISTINCT n) AS node_count, count(DISTINCT r) AS rel_count
        """
        res = cls.run_query(query)
        if res and len(res) > 0:
            return {'status': 'ONLINE', 'nodes': res[0]['node_count'], 'relationships': res[0]['rel_count']}
        return {'status': 'OFFLINE', 'nodes': 0, 'relationships': 0}

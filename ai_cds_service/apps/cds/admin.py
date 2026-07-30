from django.contrib import admin
from .models import (
    Disease, Symptom, Drug, DiseaseSymptom, DiseaseTreatment,
    DrugInteraction, CDSConversation, CDSMessage, CDSRecommendation, PromptTemplate
)

admin.site.register(Disease)
admin.site.register(Symptom)
admin.site.register(Drug)
admin.site.register(DiseaseSymptom)
admin.site.register(DiseaseTreatment)
admin.site.register(DrugInteraction)
admin.site.register(CDSConversation)
admin.site.register(CDSMessage)
admin.site.register(CDSRecommendation)
admin.site.register(PromptTemplate)

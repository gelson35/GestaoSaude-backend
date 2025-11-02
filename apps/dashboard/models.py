from django.db import models

# Tabela: RELATORIOS_GERENCIAIS
class RelatorioGerencial(models.Model):
    tipo_relatorio = models.CharField(max_length=50) # Ex: Diário, Semanal, Mensal
    data_referencia = models.DateField()
    total_ocorrencias = models.IntegerField(null=True, blank=True)
    
    # Armazena dados complexos: (ex: {"bairro_x": 10, "bairro_y": 5})
    estatistica_tipo = models.JSONField() 
    
    data_geracao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo_relatorio} - {self.data_referencia.strftime('%d/%m/%Y')}"

    class Meta:
        verbose_name = 'Relatório Gerencial'
        verbose_name_plural = 'Relatórios Gerenciais'
        db_table = 'dashboard_relatorio_gerencial'


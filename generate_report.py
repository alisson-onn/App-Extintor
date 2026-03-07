#!/usr/bin/env python3
"""
Gerador de Relatório Executivo em PDF
Sistema de Controle de Extintores - SESMT
"""

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib.colors import HexColor, white, black, grey
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from datetime import datetime
import json

# ═══════════════════════════════════════════════════════════════════════════════
# CORES CORPORATIVAS
# ═══════════════════════════════════════════════════════════════════════════════
COLOR_PRIMARY = HexColor("#1D4ED8")      # Azul corporativo
COLOR_DANGER = HexColor("#B91C1C")       # Vermelho
COLOR_WARNING = HexColor("#C2410C")      # Laranja
COLOR_SUCCESS = HexColor("#15803D")      # Verde
COLOR_NEUTRAL_DARK = HexColor("#1F2937") # Cinza escuro
COLOR_NEUTRAL_LIGHT = HexColor("#F3F4F6") # Cinza claro
COLOR_BORDER = HexColor("#D1D5DB")       # Cinza médio


class ReportGenerator:
    def __init__(self, output_path="relatorio_extintores.pdf"):
        self.output_path = output_path
        self.styles = getSampleStyleSheet()
        
    def generate(self, data):
        """Gera o PDF com os dados fornecidos"""
        doc = SimpleDocTemplate(
            self.output_path,
            pagesize=landscape(A4),
            rightMargin=15*mm,
            leftMargin=15*mm,
            topMargin=15*mm,
            bottomMargin=15*mm,
            title="Relatório Executivo - Controle de Extintores"
        )
        
        story = []
        
        # Cabeçalho
        story.extend(self._build_header(data))
        story.append(Spacer(1, 0.5*cm))
        
        # KPIs
        story.extend(self._build_kpis(data))
        story.append(Spacer(1, 0.5*cm))
        
        # Gráficos (descrição)
        story.extend(self._build_charts_section(data))
        story.append(Spacer(1, 0.5*cm))
        
        # Tabela de Extintores
        story.extend(self._build_extintor_table(data))
        story.append(Spacer(1, 0.5*cm))
        
        # Observações
        story.extend(self._build_observations(data))
        story.append(Spacer(1, 0.5*cm))
        
        # Rodapé
        story.extend(self._build_footer(data))
        
        doc.build(story)
        return self.output_path

    def _build_header(self, data):
        """Constrói o cabeçalho do relatório"""
        elements = []
        
        # Título
        title_style = ParagraphStyle(
            'TitleReport',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=COLOR_PRIMARY,
            spaceAfter=6,
            fontName='Helvetica-Bold',
            alignment=TA_CENTER
        )
        title = Paragraph("RELATÓRIO EXECUTIVO", title_style)
        elements.append(title)
        
        # Subtítulo
        subtitle_style = ParagraphStyle(
            'SubtitleReport',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=COLOR_NEUTRAL_DARK,
            spaceAfter=12,
            fontName='Helvetica',
            alignment=TA_CENTER
        )
        subtitle = Paragraph(
            "Controle e Inspeção de Extintores de Incêndio",
            subtitle_style
        )
        elements.append(subtitle)
        
        # Informações do período
        period_text = f"""
        <b>Período:</b> {data.get('period_start', 'N/A')} a {data.get('period_end', 'N/A')}<br/>
        <b>Data de Geração:</b> {datetime.now().strftime('%d/%m/%Y às %H:%M')}<br/>
        <b>Responsável:</b> {data.get('supervisor', 'Supervisor SESMT')}
        """
        period = Paragraph(period_text, self.styles['Normal'])
        elements.append(period)
        
        return elements

    def _build_kpis(self, data):
        """Constrói a seção de KPIs"""
        elements = []
        
        section_style = ParagraphStyle(
            'SectionReport',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=COLOR_PRIMARY,
            spaceAfter=8,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )
        
        title = Paragraph("INDICADORES-CHAVE DE DESEMPENHO (KPIs)", section_style)
        elements.append(title)
        
        # Dados dos KPIs
        total = data.get('total_extintores', 0)
        validos = data.get('validos', 0)
        vencidos = data.get('vencidos', 0)
        a_vencer = data.get('a_vencer', 0)
        inspecionados = data.get('inspecionados', 0)
        
        # Cálculos
        pct_validos = round((validos / total * 100) if total > 0 else 0, 1)
        pct_insp = round((inspecionados / total * 100) if total > 0 else 0, 1)
        
        # Tabela de KPIs
        kpi_data = [
            ['MÉTRICA', 'VALOR', 'PERCENTUAL', 'STATUS'],
            ['Total de Extintores', str(total), '100%', '✓'],
            ['Extintores Válidos', str(validos), f'{pct_validos}%', '✓' if vencidos == 0 else '✗'],
            ['Extintores Vencidos', str(vencidos), f'{round(vencidos/total*100, 1)}%' if total > 0 else '0%', '✗' if vencidos > 0 else '✓'],
            ['A Vencer (próx. 90 dias)', str(a_vencer), f'{round(a_vencer/total*100, 1)}%' if total > 0 else '0%', '⚠'],
            ['Inspecionados este mês', str(inspecionados), f'{pct_insp}%', '✓' if pct_insp >= 80 else '⚠'],
        ]
        
        table = Table(kpi_data, colWidths=[6*cm, 2.5*cm, 2.5*cm, 2*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), COLOR_PRIMARY),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), COLOR_NEUTRAL_LIGHT),
            ('GRID', (0, 0), (-1, -1), 1, COLOR_BORDER),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, COLOR_NEUTRAL_LIGHT]),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        elements.append(table)
        return elements

    def _build_charts_section(self, data):
        """Constrói a seção de gráficos (descrição textual)"""
        elements = []
        
        section_style = ParagraphStyle(
            'SectionReport2',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=COLOR_PRIMARY,
            spaceAfter=8,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )
        
        title = Paragraph("ANÁLISE DE STATUS", section_style)
        elements.append(title)
        
        total = data.get('total_extintores', 0)
        validos = data.get('validos', 0)
        vencidos = data.get('vencidos', 0)
        a_vencer = data.get('a_vencer', 0)
        
        # Gráfico de pizza (representação textual)
        chart_text = f"""
        <b>Distribuição de Status:</b><br/>
        • <font color="#15803D"><b>Válidos:</b> {validos} extintores ({round(validos/total*100, 1)}%)</font><br/>
        • <font color="#C2410C"><b>A Vencer:</b> {a_vencer} extintores ({round(a_vencer/total*100, 1)}%)</font><br/>
        • <font color="#B91C1C"><b>Vencidos:</b> {vencidos} extintores ({round(vencidos/total*100, 1)}%)</font><br/>
        """
        
        chart = Paragraph(chart_text, self.styles['Normal'])
        elements.append(chart)
        
        return elements

    def _build_extintor_table(self, data):
        """Constrói a tabela de extintores"""
        elements = []
        
        section_style = ParagraphStyle(
            'SectionReport3',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=COLOR_PRIMARY,
            spaceAfter=8,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )
        
        title = Paragraph("RELAÇÃO DE EXTINTORES INSPECIONADOS", section_style)
        elements.append(title)
        
        # Cabeçalho da tabela
        table_data = [
            ['ID', 'Área', 'Local', 'Tipo', 'Próx. Recarga', 'Status', 'Dias p/ Vencer']
        ]
        
        # Dados dos extintores
        extintores = data.get('extintores', [])
        for ext in extintores[:30]:  # Limita a 30 para não ficar muito grande
            status_symbol = '✓' if ext['status'] == 'Válido' else '⚠' if ext['status'] == 'Próximo ao vencimento' else '✗'
            table_data.append([
                ext.get('id', 'N/A')[:15],
                str(ext.get('area', 'N/A')),
                ext.get('local', 'N/A')[:20],
                ext.get('tipo', 'N/A')[:15],
                ext.get('proxima_recarga', 'N/A'),
                f"{status_symbol} {ext.get('status', 'N/A')}",
                str(ext.get('dias_vencer', 'N/A'))
            ])
        
        # Se houver mais de 30, adiciona nota
        if len(extintores) > 30:
            table_data.append(['...', '...', f'Total: {len(extintores)} extintores', '...', '...', '...', '...'])
        
        table = Table(table_data, colWidths=[2*cm, 1.2*cm, 3*cm, 2.2*cm, 2.2*cm, 2.2*cm, 1.8*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), COLOR_PRIMARY),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, COLOR_NEUTRAL_LIGHT]),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        elements.append(table)
        return elements

    def _build_observations(self, data):
        """Constrói a seção de observações"""
        elements = []
        
        section_style = ParagraphStyle(
            'SectionReport4',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=COLOR_PRIMARY,
            spaceAfter=8,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )
        
        title = Paragraph("OBSERVAÇÕES E RECOMENDAÇÕES", section_style)
        elements.append(title)
        
        obs = data.get('observations', [])
        
        if obs:
            obs_text = "<br/>".join([f"• {o}" for o in obs])
        else:
            obs_text = "Nenhuma observação crítica registrada."
        
        obs_para = Paragraph(obs_text, self.styles['Normal'])
        elements.append(obs_para)
        
        return elements

    def _build_footer(self, data):
        """Constrói o rodapé do relatório"""
        elements = []
        
        footer_text = f"""
        <b>Técnicos Responsáveis:</b> {', '.join(data.get('tecnicos', ['N/A']))}<br/>
        <b>Supervisor:</b> {data.get('supervisor', 'N/A')}<br/>
        <b>Gerado em:</b> {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}<br/>
        <i>Este é um documento confidencial destinado apenas para uso interno.</i>
        """
        
        footer = Paragraph(footer_text, self.styles['Normal'])
        elements.append(footer)
        
        return elements


def main():
    """Função principal para teste"""
    # Dados de exemplo
    sample_data = {
        'period_start': '01/03/2026',
        'period_end': '31/03/2026',
        'supervisor': 'Eng. João Silva',
        'tecnicos': ['Carlos', 'Pedro', 'Ana', 'Marcus'],
        'total_extintores': 384,
        'validos': 350,
        'vencidos': 8,
        'a_vencer': 26,
        'inspecionados': 280,
        'observations': [
            'Extintor A1-3 vencido em Área 1 - Ação imediata necessária',
            'Área 5 com 85% de inspeção - Finalizar até 05/04',
            'Manutenção preventiva agendada para Área 3 em 15/04'
        ],
        'extintores': [
            {
                'id': 'A1-001',
                'area': 1,
                'local': 'Corredor principal',
                'tipo': 'AP-10L',
                'proxima_recarga': '15/06/2026',
                'status': 'Válido',
                'dias_vencer': 101
            },
            {
                'id': 'A1-002',
                'area': 1,
                'local': 'Sala de reuniões',
                'tipo': 'CO2-4KG',
                'proxima_recarga': '10/04/2026',
                'status': 'Próximo ao vencimento',
                'dias_vencer': 35
            },
            {
                'id': 'A1-003',
                'area': 1,
                'local': 'Cozinha',
                'tipo': 'PQS BC-6KG',
                'proxima_recarga': '25/02/2026',
                'status': 'Vencido',
                'dias_vencer': -9
            },
        ]
    }
    
    generator = ReportGenerator("relatorio_teste.pdf")
    output = generator.generate(sample_data)
    print(f"Relatório gerado com sucesso: {output}")


if __name__ == "__main__":
    main()

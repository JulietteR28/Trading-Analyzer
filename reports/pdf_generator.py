"""
Module PDFGenerator - Generation de rapports PDF
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
import os


class PDFGenerator:
    """
    Classe pour generer des rapports PDF
    
    Fonctionnalites:
    - Page de couverture
    - Tableaux de donnees
    - Insertion de graphiques
    - Texte formate
    """
    
    def __init__(self, filename: str = "rapport.pdf"):
        """
        Initialise le PDFGenerator
        
        Args:
            filename (str): Nom du fichier PDF a creer
        """
        # Creer le dossier exports s'il n'existe pas
        os.makedirs('data/exports', exist_ok=True)
        
        self.filename = f"data/exports/{filename}"
        self.story = []  # Contenu du PDF
        self.styles = getSampleStyleSheet()
        
        # Creer des styles personnalises
        self._create_custom_styles()
        
        print(f" PDFGenerator initialise: {self.filename}")
    
    def _create_custom_styles(self):
        """Cree des styles personnalises pour le PDF"""
        # Style pour le titre principal
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Style pour les sous-titres
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2e5c8a'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        # Style pour le texte normal
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=10,
            alignment=TA_LEFT
        ))
    
    def add_title_page(self, title: str, subtitle: str = ""):
        """
        Ajoute une page de couverture
        
        Args:
            title (str): Titre principal
            subtitle (str): Sous-titre optionnel
        """
        print("  Ajout de la page de couverture...")
        
        # Espacements
        self.story.append(Spacer(1, 5*cm))
        
        # Titre principal
        title_para = Paragraph(title, self.styles['CustomTitle'])
        self.story.append(title_para)
        
        # Sous-titre si fourni
        if subtitle:
            subtitle_para = Paragraph(subtitle, self.styles['Heading3'])
            self.story.append(Spacer(1, 1*cm))
            self.story.append(subtitle_para)
        
        # Date
        date_str = datetime.now().strftime("%d/%m/%Y")
        date_para = Paragraph(f"<para align=center>Date: {date_str}</para>", 
                             self.styles['Normal'])
        self.story.append(Spacer(1, 2*cm))
        self.story.append(date_para)
        
        # Saut de page
        self.story.append(PageBreak())
        
        print("  Page de couverture ajoutee")
    
    def add_heading(self, text: str):
        """
        Ajoute un titre de section
        
        Args:
            text (str): Texte du titre
        """
        para = Paragraph(text, self.styles['CustomHeading'])
        self.story.append(para)
        self.story.append(Spacer(1, 0.3*cm))
    
    def add_text(self, text: str):
        """
        Ajoute du texte simple
        
        Args:
            text (str): Texte a ajouter
        """
        para = Paragraph(text, self.styles['CustomBody'])
        self.story.append(para)
    
    def add_table(self, data: list, col_widths: list = None):
        """
        Ajoute un tableau
        
        Args:
            data (list): Liste de listes pour les lignes du tableau
            col_widths (list): Largeurs des colonnes (optionnel)
        """
        print(f"  Ajout d'un tableau ({len(data)} lignes)...")
        
        # Creer le tableau
        table = Table(data, colWidths=col_widths)
        
        # Style du tableau
        table.setStyle(TableStyle([
            # En-tete
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Corps du tableau
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
            
            # Bordures
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 0.5*cm))
        
        print("   Tableau ajoute")
    
    def add_image(self, image_path: str, width: float = 20*cm, height: float = 8*cm):
        """
        Ajoute une image (graphique)
        
        Args:
            image_path (str): Chemin vers l'image
            width (float): Largeur de l'image
            height (float): Hauteur maximale de l'image
        """
        if not os.path.exists(image_path):
            print(f"   Image introuvable: {image_path}")
            return
        
        print(f"  Ajout de l'image: {os.path.basename(image_path)}...")
        
        # Creer l'objet Image avec largeur ET hauteur fixes
        img = Image(image_path, width=width, height=height)
        
        self.story.append(img)
        self.story.append(Spacer(1, 0.5*cm))
        
        print("   Image ajoutee")
    
    def add_spacer(self, height: float = 1*cm):
        """
        Ajoute un espace vertical
        
        Args:
            height (float): Hauteur de l'espace
        """
        self.story.append(Spacer(1, height))
    
    def add_page_break(self):
        """Ajoute un saut de page"""
        self.story.append(PageBreak())
    
    def generate(self):
        """
        Genere le fichier PDF final
        
        Returns:
            str: Chemin du fichier genere
        """
        print(f"\nGeneration du PDF: {self.filename}")
        
        # Creer le document
        doc = SimpleDocTemplate(
            self.filename,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # Generer le PDF
        doc.build(self.story)
        
        print(f" PDF genere avec succes: {self.filename}")
        return self.filename
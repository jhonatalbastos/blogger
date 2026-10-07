import os
import json
import random
import requests
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# --- CONFIGURAÇÕES ---
BLOG_ID = os.environ.get("BLOGGER_ID")
PEXELS_KEY = os.environ.get("PEXELS_API_KEY")
AMAZON_TAG = os.environ.get("AMAZON_TAG", "seuid-20")  # Configure no Secret se tiver

# Lista de livros para rodízio ou inspiração (pode expandir como quiser)
LIVROS_CATALOGO = [
    {"titulo": "O Homem Mais Rico da Babilônia", "autor": "George S. Clason", "termo_pexels": "ancient coins books reading"},
    {"titulo": "Hábitos Atômicos", "autor": "James Clear", "termo_pexels": "routine focus workspace notes"},
    {"titulo": "A Coragem de Ser Imperfeito", "autor": "Brené Brown", "termo_pexels": "calm reflection coffee journal"},
    {"titulo": "Essencialismo", "autor": "Greg McKeown", "termo_pexels": "minimalist desk workspace clean"},
    {"titulo": "Rápido e Devagar: Duas Formas de Pensar", "autor": "Daniel Kahneman", "termo_pexels": "brain study concentration books"},
    {"titulo": "A Psicologia do Financeiro", "autor": "Morgan Housel", "termo_pexels": "finance savings planning read"},
    {"titulo": "Antifrágil", "autor": "Nassim Nicholas Taleb", "termo_pexels": "strength strategy reading library"}
]

def obter_capa_google_books(titulo, autor):
    """Busca a capa do livro e ISBN via API pública do Google Books."""
    url = f"https://www.googleapis.com/books/v1/volumes?q=intitle:{titulo}+inauthor:{autor}"
    res = requests.get(url).json()
    
    capa_url = None
    isbn = None
    descricao = ""
    
    if "items" in res and len(res["items"]) > 0:
        livro = res["items"][0]["volumeInfo"]
        imagens = livro.get("imageLinks", {})
        # Pega a melhor resolução disponível
        capa_url = imagens.get("extraLarge") or imagens.get("large") or imagens.get("medium") or imagens.get("thumbnail")
        if capa_url:
            capa_url = capa_url.replace("http://", "https://")
        
        descricao = livro.get("description", "")
        identificadores = livro.get("industryIdentifiers", [])
        for ident in identificadores:
            if ident.get("type") in ["ISBN_13", "ISBN_10"]:
                isbn = ident.get("identifier")
                break
                
    return capa_url, isbn, descricao

def obter_foto_pexels(termo_busca):
    """Busca uma imagem conceitual de alta qualidade no Pexels."""
    if not PEXELS_KEY:
        return None
    url = f"https://api.pexels.com/v1/search?query={termo_busca}&per_page=15&orientation=landscape"
    headers = {"Authorization": PEXELS_KEY}
    res = requests.get(url, headers=headers).json()
    
    photos = res.get("photos", [])
    if photos:
        foto_escolhida = random.choice(photos)
        return foto_escolhida["src"].get("large2x") or foto_escolhida["src"].get("large")
    return None

def gerar_link_amazon(titulo, autor, isbn=None):
    """Gera o link de afiliado para o livro."""
    if isbn:
        return f"https://www.amazon.com.br/dp/{isbn}?tag={AMAZON_TAG}"
    termo = requests.utils.quote(f"{titulo} {autor}")
    return f"https://www.amazon.com.br/s?k={termo}&tag={AMAZON_TAG}"

def montar_post_html(livro, capa_url, foto_pexels, link_afiliado):
    """Estrutura o artigo em HTML com design limpo e responsivo."""
    titulo = livro["titulo"]
    autor = livro["autor"]
    
    html = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.8; color: #2d3748; max-width: 720px; margin: 0 auto;">
        
        {f'<div style="text-align: center; margin-bottom: 30px;"><img src="{capa_url}" alt="Capa do livro {titulo}" style="max-height: 420px; border-radius: 8px; box-shadow: 0 10px 25px rgba(0,0,0,0.15);"/></div>' if capa_url else ''}
        
        <p style="font-size: 1.15em; color: #4a5568;">
            Quando comecei as primeiras páginas de <strong>{titulo}</strong>, de <em>{autor}</em>, minha expectativa era encontrar mais um apanhado de conselhos batidos. O que me surpreendeu, no entanto, foi o impacto direto que a leitura causou na minha rotina logo na primeira semana.
        </p>

        <h3 style="color: #1a202c; margin-top: 35px; border-bottom: 2px solid #edf2f7; padding-bottom: 8px;">Pontos que transformaram minha percepção</h3>
        <p>
            O diferencial da abordagem de {autor} está na clareza com que desmonta hábitos contraproducentes que mantemos no piloto automático. Mais do que teoria, o livro traz um roteiro aplicável para quem quer organizar os pensamentos e priorizar o que realmente traz retorno prático.
        </p>

        {f'<div style="margin: 35px 0; text-align: center;"><img src="{foto_pexels}" alt="Ambiente de foco e leitura" style="width: 100%; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.08);"/></div>' if foto_pexels else ''}

        <h3 style="color: #1a202c; margin-top: 35px; border-bottom: 2px solid #edf2f7; padding-bottom: 8px;">Vale a pena ler?</h3>
        <p>
            Sem rodeios: é uma leitura indispensável se você busca clareza mental e ferramentas reais para aprimorar sua disciplina e tomada de decisão no dia a dia.
        </p>

        <div style="margin-top: 40px; padding: 25px; background-color: #f7fafc; border-left: 4px solid #3182ce; border-radius: 4px; text-align: center;">
            <p style="margin: 0 0 15px 0; font-weight: 600; font-size: 1.05em; color: #2b6cb0;">Quer garantir o seu exemplar físico ou Kindle?</p>
            <a href="{link_afiliado}" target="_blank" rel="noopener noreferrer" style="display: inline-block; background-color: #ff9900; color: #111; font-weight: bold; text-decoration: none; padding: 12px 28px; border-radius: 6px; box-shadow: 0 2px 5px rgba(0,0,0,0.15);">
                Ver "{titulo}" na Amazon
            </a>
        </div>
    </div>
    """
    return html

def publicar_no_blogger(titulo_post, conteudo_html):
    """Autentica via token e insere o post no Blogger."""
    token_info = json.loads(os.environ["BLOGGER_TOKEN_JSON"])
    creds = Credentials.from_authorized_user_info(token_info)

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

    service = build("blogger", "v3", credentials=creds)

    corpo = {
        "kind": "blogger#post",
        "title": titulo_post,
        "content": conteudo_html,
        "labels": ["Resenha", "Desenvolvimento Pessoal", "Livros"]
    }

    post = service.posts().insert(blogId=BLOG_ID, body=corpo, isDraft=False).execute()
    print(f"Post publicado com sucesso! URL: {post.get('url')}")

def executar():
    livro = random.choice(LIVROS_CATALOGO)
    print(f"Processando resenha de: {livro['titulo']}...")

    capa_url, isbn, _ = obter_capa_google_books(livro["titulo"], livro["autor"])
    foto_pexels = obter_foto_pexels(livro["termo_pexels"])
    link_amazon = gerar_link_amazon(livro["titulo"], livro["autor"], isbn)

    titulo_post = f"Minhas Reflexões sobre '{livro['titulo']}' ({livro['autor']})"
    html = montar_post_html(livro, capa_url, foto_pexels, link_amazon)

    publicar_no_blogger(titulo_post, html)

if __name__ == "__main__":
    executar()

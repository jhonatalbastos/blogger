import os
import json
import random
import requests
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# --- CONFIGURAÇÕES BÁSICAS ---
BLOG_ID = os.environ.get("BLOGGER_ID")
PEXELS_KEY = os.environ.get("PEXELS_API_KEY")
AMAZON_TAG = os.environ.get("AMAZON_TAG", "seuid-20")

# Catálogo de livros para rodízio automático
LIVROS_CATALOGO = [
    {
        "titulo": "O Homem Mais Rico da Babilônia",
        "autor": "George S. Clason",
        "termo_pexels": "ancient coins books reading"
    },
    {
        "titulo": "Hábitos Atômicos",
        "autor": "James Clear",
        "termo_pexels": "routine focus workspace notes"
    },
    {
        "titulo": "A Coragem de Ser Imperfeito",
        "autor": "Brené Brown",
        "termo_pexels": "calm reflection coffee journal"
    },
    {
        "titulo": "Essencialismo",
        "autor": "Greg McKeown",
        "termo_pexels": "minimalist desk workspace clean"
    },
    {
        "titulo": "Rápido e Devagar: Duas Formas de Pensar",
        "autor": "Daniel Kahneman",
        "termo_pexels": "brain study concentration books"
    },
    {
        "titulo": "A Psicologia do Financeiro",
        "autor": "Morgan Housel",
        "termo_pexels": "finance savings planning read"
    },
    {
        "titulo": "Antifrágil",
        "autor": "Nassim Nicholas Taleb",
        "termo_pexels": "strength strategy reading library"
    }
]

def obter_capa_google_books(titulo, autor):
    """Busca a capa do livro e o ISBN via API pública do Google Books."""
    capa_url = None
    isbn = None
    descricao = ""
    try:
        url = f"https://www.googleapis.com/books/v1/volumes?q=intitle:{titulo}+inauthor:{autor}"
        res = requests.get(url, timeout=15).json()

        if "items" in res and len(res["items"]) > 0:
            livro = res["items"][0].get("volumeInfo", {})
            imagens = livro.get("imageLinks", {})

            capa_url = (
                imagens.get("extraLarge")
                or imagens.get("large")
                or imagens.get("medium")
                or imagens.get("thumbnail")
            )
            if capa_url:
                capa_url = capa_url.replace("http://", "https://")

            descricao = livro.get("description", "")
            for ident in livro.get("industryIdentifiers", []):
                if ident.get("type") in ["ISBN_13", "ISBN_10"]:
                    isbn = ident.get("identifier")
                    break
    except Exception as erro:
        print(f"Aviso ao consultar Google Books: {erro}")

    return capa_url, isbn, descricao

def obter_foto_pexels(termo_busca):
    """Busca uma imagem temática em alta resolução no Pexels."""
    if not PEXELS_KEY:
        return None
    try:
        url = f"https://api.pexels.com/v1/search?query={termo_busca}&per_page=15&orientation=landscape"
        headers = {"Authorization": PEXELS_KEY}
        res = requests.get(url, headers=headers, timeout=15).json()

        photos = res.get("photos", [])
        if photos:
            foto_escolhida = random.choice(photos)
            return foto_escolhida["src"].get("large2x") or foto_escolhida["src"].get("large")
    except Exception as erro:
        print(f"Aviso ao consultar Pexels: {erro}")
    return None

def gerar_link_amazon(titulo, autor, isbn=None):
    """Monta o link de afiliado da Amazon."""
    if isbn:
        return f"https://www.amazon.com.br/dp/{isbn}?tag={AMAZON_TAG}"
    termo = requests.utils.quote(f"{titulo} {autor}")
    return f"https://www.amazon.com.br/s?k={termo}&tag={AMAZON_TAG}"

def montar_post_html(livro, capa_url, foto_pexels, link_afiliado):
    """Gera a estrutura HTML limpa e responsiva do artigo."""
    titulo = livro["titulo"]
    autor = livro["autor"]

    bloco_capa = (
        f'<div style="text-align: center; margin-bottom: 30px;">'
        f'<img src="{capa_url}" alt="Capa do livro {titulo}" style="max-height: 420px; border-radius: 8px; box-shadow: 0 10px 25px rgba(0,0,0,0.15);"/>'
        f'</div>'
        if capa_url else ''
    )

    bloco_pexels = (
        f'<div style="margin: 35px 0; text-align: center;">'
        f'<img src="{foto_pexels}" alt="Ambiente de leitura" style="width: 100%; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.08);"/>'
        f'</div>'
        if foto_pexels else ''
    )

    html = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.8; color: #2d3748; max-width: 720px; margin: 0 auto;">
        
        {bloco_capa}

        <p style="font-size: 1.15em; color: #4a5568;">
            Quando iniciei as primeiras páginas de <strong>{titulo}</strong>, de <em>{autor}</em>, minha expectativa era encontrar mais um apanhado de conselhos batidos. O que me surpreendeu, no entanto, foi o impacto direto que a leitura causou na minha rotina e organização logo nos primeiros dias.
        </p>

        <h3 style="color: #1a202c; margin-top: 35px; border-bottom: 2px solid #edf2f7; padding-bottom: 8px;">Pontos que transformaram minha percepção</h3>
        <p>
            O diferencial da abordagem de {autor} está na clareza com que desconstrói hábitos contraproducentes mantidos no piloto automático. Mais do que teoria, o livro traz um roteiro aplicável para quem deseja organizar os pensamentos e priorizar o que realmente traz retorno prático.
        </p>

        {bloco_pexels}

        <h3 style="color: #1a202c; margin-top: 35px; border-bottom: 2px solid #edf2f7; padding-bottom: 8px;">Vale a pena a leitura?</h3>
        <p>
            Sem rodeios: é uma leitura indispensável se você busca clareza mental e ferramentas reais para aprimorar sua disciplina e tomada de decisão no dia a dia.
        </p>

        <div style="margin-top: 40px; padding: 25px; background-color: #f7fafc; border-left: 4px solid #3182ce; border-radius: 4px; text-align: center;">
            <p style="margin: 0 0 15px 0; font-weight: 600; font-size: 1.05em; color: #2b6cb0;">Gostou da recomendação? Garanta o seu exemplar:</p>
            <a href="{link_afiliado}" target="_blank" rel="noopener noreferrer" style="display: inline-block; background-color: #ff9900; color: #111; font-weight: bold; text-decoration: none; padding: 12px 28px; border-radius: 6px; box-shadow: 0 2px 5px rgba(0,0,0,0.15);">
                Ver "{titulo}" na Amazon
            </a>
        </div>
    </div>
    """
    return html

def publicar_no_blogger(titulo_post, conteudo_html):
    """Carrega o token de autenticação e envia o artigo para a Blogger API."""
    if not BLOG_ID:
        raise ValueError("A variável BLOGGER_ID não está configurada.")

    raw_token = os.environ.get("BLOGGER_TOKEN_JSON")
    if not raw_token or not raw_token.strip():
        raise ValueError(
            "O secret BLOGGER_TOKEN_JSON está vazio ou ausente! "
            "Confira se o nome está idêntico em Settings > Secrets and variables > Actions."
        )

    token_info = json.loads(raw_token)
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
    print(f"\nPost publicado com sucesso!\nURL: {post.get('url')}")

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

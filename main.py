import os
import json
import random
import requests
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# --- CONFIGURAÇÕES DE AMBIENTE ---
BLOG_ID = os.environ.get("BLOGGER_ID")
PEXELS_KEY = os.environ.get("PEXELS_API_KEY")
AMAZON_TAG = os.environ.get("AMAZON_TAG", "seuid-20")

# Catálogo completo com temas, palavras-chave para fotos e suporte a capa manual
LIVROS_CATALOGO = [
    {
        "titulo": "Hábitos Atômicos",
        "subtitulo": "Um Método Fácil e Comprovado de Construir Bons Hábitos e Romper com os Maus",
        "autor": "James Clear",
        "termos_pexels": ["workspace minimalist desk", "morning routine coffee journal", "running watch fitness athlete"],
        "capa_manual": "" # Se quiser forçar uma URL de capa, cole aqui
    },
    {
        "titulo": "O Homem Mais Rico da Babilônia",
        "subtitulo": "Os Segredos do Sucesso dos Antigos para Conquistar a Riqueza",
        "autor": "George S. Clason",
        "termos_pexels": ["ancient architecture column", "gold coins savings investment", "library books study desk"],
        "capa_manual": ""
    },
    {
        "titulo": "Essencialismo",
        "subtitulo": "A Disciplinada Busca por Menos",
        "autor": "Greg McKeown",
        "termos_pexels": ["minimalist interior clean room", "declutter workspace notebook", "quiet nature forest path"],
        "capa_manual": ""
    },
    {
        "titulo": "Rápido e Devagar: Duas Formas de Pensar",
        "subtitulo": "As Forças Invisíveis que Moldam Nossas Escolhas",
        "autor": "Daniel Kahneman",
        "termos_pexels": ["chess board strategic play", "brain neurology focus study", "decision crossroads path road"],
        "capa_manual": ""
    },
    {
        "titulo": "A Psicologia Financeira",
        "subtitulo": "Lições Atemporais sobre Fortuna, Ganância e Felicidade",
        "autor": "Morgan Housel",
        "termos_pexels": ["financial charts investment office", "lifestyle peaceful home coffee", "old ledger cash planning"],
        "capa_manual": ""
    },
    {
        "titulo": "Antifrágil",
        "subtitulo": "Coisas que se Beneficiam com o Caos",
        "autor": "Nassim Nicholas Taleb",
        "termos_pexels": ["storm ocean waves rocks", "weightlifting iron gym strength", "ancient sculpture philosophy"],
        "capa_manual": ""
    }
]

def obter_capa_livro(titulo, autor, capa_manual=""):
    """Obtém a melhor capa disponível via URL manual ou Google Books API."""
    if capa_manual and capa_manual.startswith("http"):
        return capa_manual, None, ""

    capa_url = None
    isbn = None
    descricao = ""

    try:
        url = f"https://www.googleapis.com/books/v1/volumes?q=intitle:{requests.utils.quote(titulo)}+inauthor:{requests.utils.quote(autor)}"
        res = requests.get(url, timeout=15).json()

        if "items" in res and len(res["items"]) > 0:
            volume_info = res["items"][0].get("volumeInfo", {})
            imagens = volume_info.get("imageLinks", {})

            # Busca pela imagem de maior resolução
            capa_url = (
                imagens.get("extraLarge")
                or imagens.get("large")
                or imagens.get("medium")
                or imagens.get("small")
                or imagens.get("thumbnail")
            )

            if capa_url:
                capa_url = capa_url.replace("http://", "https://")
                # Remove parâmetros de miniatura para obter a imagem em tamanho integral
                capa_url = capa_url.replace("&edge=curl", "").replace("zoom=1", "zoom=3")

            descricao = volume_info.get("description", "")
            for ident in volume_info.get("industryIdentifiers", []):
                if ident.get("type") in ["ISBN_13", "ISBN_10"]:
                    isbn = ident.get("identifier")
                    break
    except Exception as erro:
        print(f"Erro ao buscar dados no Google Books: {erro}")

    return capa_url, isbn, descricao

def obter_multiplas_fotos_pexels(termos):
    """Busca 3 imagens de alta qualidade no Pexels para acompanhar o texto longo."""
    fotos = []
    if not PEXELS_KEY:
        return [None, None, None]

    headers = {"Authorization": PEXELS_KEY}
    for termo in termos:
        try:
            url = f"https://api.pexels.com/v1/search?query={termo}&per_page=10&orientation=landscape"
            res = requests.get(url, headers=headers, timeout=15).json()
            photos_data = res.get("photos", [])
            if photos_data:
                escolhida = random.choice(photos_data)
                url_foto = escolhida["src"].get("large2x") or escolhida["src"].get("large")
                fotos.append(url_foto)
            else:
                fotos.append(None)
        except Exception:
            fotos.append(None)

    while len(fotos) < 3:
        fotos.append(None)

    return fotos

def gerar_link_amazon(titulo, autor, isbn=None):
    if isbn:
        return f"https://www.amazon.com.br/dp/{isbn}?tag={AMAZON_TAG}"
    termo = requests.utils.quote(f"{titulo} {autor}")
    return f"https://www.amazon.com.br/s?k={termo}&tag={AMAZON_TAG}"

def gerar_artigo_completo(livro, capa_url, fotos_pexels, link_afiliado):
    """Gera um artigo robusto (+1000 palavras) com diagramação editorial."""
    t = livro["titulo"]
    st = livro.get("subtitulo", "")
    a = livro["autor"]
    img1, img2, img3 = fotos_pexels

    bloco_capa_destaque = f"""
    <div style="text-align: center; margin: 40px auto 45px auto; max-width: 360px;">
        <div style="background: #ffffff; padding: 14px; border-radius: 12px; box-shadow: 0 18px 38px rgba(0,0,0,0.18), 0 5px 12px rgba(0,0,0,0.08); transition: transform 0.3s ease;">
            <img src="{capa_url}" alt="Capa oficial do livro {t}" style="width: 100%; height: auto; border-radius: 8px; display: block; object-fit: cover; aspect-ratio: 2/3;" />
        </div>
        <p style="font-size: 0.88em; color: #718096; margin-top: 12px; font-style: italic;">Edição física / digital de <strong>{t}</strong> ({a})</p>
    </div>
    """ if capa_url else ""

    bloco_img1 = f"""
    <div style="margin: 45px 0; text-align: center;">
        <img src="{img1}" alt="Ambiente de reflexão e leitura" style="width: 100%; border-radius: 10px; box-shadow: 0 8px 24px rgba(0,0,0,0.09); margin-bottom: 8px;" />
        <span style="font-size: 0.85em; color: #a0aec0; letter-spacing: 0.5px;">Registro conceitual: foco, processo e rotina diária</span>
    </div>
    """ if img1 else ""

    bloco_img2 = f"""
    <div style="margin: 45px 0; text-align: center;">
        <img src="{img2}" alt="Construção de hábitos e disciplina" style="width: 100%; border-radius: 10px; box-shadow: 0 8px 24px rgba(0,0,0,0.09); margin-bottom: 8px;" />
        <span style="font-size: 0.85em; color: #a0aec0; letter-spacing: 0.5px;">Consistência: pequenos blocos sustentam grandes estruturas</span>
    </div>
    """ if img2 else ""

    bloco_img3 = f"""
    <div style="margin: 45px 0; text-align: center;">
        <img src="{img3}" alt="Visão de longo prazo" style="width: 100%; border-radius: 10px; box-shadow: 0 8px 24px rgba(0,0,0,0.09); margin-bottom: 8px;" />
        <span style="font-size: 0.85em; color: #a0aec0; letter-spacing: 0.5px;">Estratégia e lucidez para o longo prazo</span>
    </div>
    """ if img3 else ""

    html = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.95; color: #2d3748; max-width: 780px; margin: 0 auto; font-size: 1.08em;">
        
        <p style="font-size: 1.25em; color: #4a5568; line-height: 1.7; font-weight: 300; border-left: 3px solid #3182ce; padding-left: 18px; margin-bottom: 30px;">
            Muitos livros prometem transformar rotinas da noite para o dia com fórmulas milagrosas. Poucos têm a sobriedade de admitir que a transformação verdadeira é um processo silencioso, gradual e, por vezes, profundamente desconfortável. <em>{t}</em> pertence a este segundo e raro grupo.
        </p>

        {bloco_capa_destaque}

        <h2 style="color: #1a202c; font-size: 1.6em; border-bottom: 2px solid #edf2f7; padding-bottom: 12px; margin-top: 50px;">
            1. O ponto de partida: Por que decidi revisitar esta obra?
        </h2>
        <p>
            Existe um momento no ano em que o acúmulo de compromissos operacionais, projetos em paralelo e distrações diárias parece exigir uma pausa estratégica. Nós começamos dezenas de tarefas com elevado entusiasmo, mas a energia inicial inevitavelmente se dissipa quando a rotina cinzenta se instala. Foi exatamente buscando um freio de arrumação e um método estruturado que peguei <strong>{t}</strong>, obra marcante de <em>{a}</em>.
        </p>
        <p>
            Minha abordagem inicial foi intencionalmente crítica. Na era dos resumos de quinze minutos e das soluções pré-fabricadas das redes sociais, a maioria dos títulos modernos acaba soando como repetição diluída de estoicismo ou psicologia comportamental rasa. Contudo, desde os primeiros capítulos, fica evidente o rigor do autor: ele não se apoia em jargões de autoajuda ou discursos motivacionais inflamados, mas sim em mecânicas claras de causa e consequência.
        </p>
        <p>
            O cerne da tese apresentada é direto: não somos definidos por nossos grandes saltos esporádicos, mas pelo sistema silencioso que opera por trás das nossas horas comuns. Se você não tem controle consciente sobre as pequenas ações repetidas todos os dias, a ambição vira apenas uma fonte recorrente de frustração.
        </p>

        {bloco_img1}

        <h2 style="color: #1a202c; font-size: 1.6em; border-bottom: 2px solid #edf2f7; padding-bottom: 12px; margin-top: 50px;">
            2. Desconstruindo o método: As ideias que realmente importam
        </h2>
        <p>
            Ao dissecar as páginas de <em>{t}</em>, um aspecto central se sobressai: a distinção fundamental entre metas e sistemas. Estabelecer um objetivo claro tem o seu valor para definir a direção do barco, mas é a qualidade do remo e a cadência das remadas que determinam se você vai cruzar a correnteza ou ficar girando em círculos.
        </p>
        <p>
            O autor nos mostra como tendemos a romantizar o momento da conquista — a aprovação, a entrega do grande projeto, o corpo em forma, a meta financeira batida —, esquecendo que esse evento é apenas o subproduto de um arranjo mecânico sustentado por meses a fio. Quando focamos exclusivamente no desfecho final, condicionamos nossa satisfação a um marco futuro que pode demorar anos para chegar, tornando o percurso árduo e desgastante.
        </p>
        
        <blockquote style="margin: 35px 0; padding: 20px 25px; background-color: #f7fafc; border-left: 4px solid #4a5568; font-style: italic; color: #2d3748; border-radius: 0 8px 8px 0;">
            "Você não sobe ao nível de suas metas; você cai ao nível dos seus sistemas de suporte."
        </blockquote>

        <p>
            Outro ponto de virada na leitura é a relação entre identidade e hábitos. {a} demonstra com precisão cirúrgica que tentar mudar um comportamento apenas pela força de vontade bruta é uma estratégia fadada ao esgotamento mental. A força de vontade é um recurso finito: ela se desgasta ao longo do dia com decisões triviais, estresse do trabalho e imprevistos cotidianos. A única forma duradoura de sustentar uma disciplina rigorosa é fazer com que o comportamento desejado esteja alinhado àquilo que você genuinamente acredita sobre si mesmo.
        </p>

        {bloco_img2}

        <h2 style="color: #1a202c; font-size: 1.6em; border-bottom: 2px solid #edf2f7; padding-bottom: 12px; margin-top: 50px;">
            3. Aplicação prática no mundo real: Onde a teoria encontra o chão de fábrica
        </h2>
        <p>
            O maior mérito de um livro reside na facilidade com que ele resiste à segunda-feira de manhã. Enquanto muitas obras conceituais evaporam assim que fechamos a contracapa, os ensinamentos de {t} têm aplicabilidade imediata tanto na gestão pessoal de tempo quanto na execução de projetos profissionais complexos.
        </p>
        <p>
            Na prática, comecei aplicando a regra do atrito: eliminar qualquer obstáculo mínimo entre mim e o trabalho focado que precisa ser realizado, enquanto crio barreiras intencionais para as distrações automáticas. Se o ambiente físico e digital não for blindado com antecedência, a dispersão vence por inércia.
        </p>
        <p>
            Outra implementação que gerou dividendos imediatos foi o empilhamento de rotinas: atrelar uma obrigação exigente a um hábito já sedimentado no cotidiano. Isso reduz o custo cognitivo de ter que "decidir" quando começar. A ação simplesmente acontece porque está ancorada em uma sequência pré-definida e previsível.
        </p>

        {bloco_img3}

        <h2 style="color: #1a202c; font-size: 1.6em; border-bottom: 2px solid #edf2f7; padding-bottom: 12px; margin-top: 50px;">
            4. Nem tudo são flores: Pontos de crítica e reflexão
        </h2>
        <p>
            Uma análise honesta não pode se limitar a elogios incondicionais. Embora o livro seja excepcional em sua estrutura lógica, ele por vezes passa a impressão de que a vida humana pode ser inteiramente reduzida a planilhas de otimização e processos de engenharia industrial.
        </p>
        <p>
            O excesso de métricas e controle pode, se não for dosado com maturidade, gerar uma ansiedade desnecessária em períodos imprevisíveis ou de crise legítima — momentos em que a flexibilidade, o descanso e o silêncio são muito mais urgentes do que o cumprimento cego de metas de eficiência. Vale absorver as ferramentas pragmáticas do autor sem cair na armadilha da neurose da produtividade ininterrupta.
        </p>

        <h2 style="color: #1a202c; font-size: 1.6em; border-bottom: 2px solid #edf2f7; padding-bottom: 12px; margin-top: 50px;">
            5. Veredito: Para quem vale a pena ler?
        </h2>
        <p>
            Se você se encontra cansado de ciclos recorrentes de entusiasmo passageiro seguido de paralisia, ou se busca clareza operacional para tocar seus objetivos com serenidade e consistência, <strong>{t}</strong> é uma leitura indispensável. Não se trata de ler depressa para adicionar mais um título à sua lista anual, mas de estudar suas páginas com um lápis na mão e aplicar as lições no seu ritmo.
        </p>

        <div style="margin-top: 55px; padding: 35px 30px; background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%); border-left: 5px solid #ff9900; border-radius: 8px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.04);">
            <h3 style="margin: 0 0 12px 0; color: #1a202c; font-size: 1.3em;">Deseja aprofundar sua leitura com o livro em mãos?</h3>
            <p style="margin: 0 0 25px 0; color: #4a5568; font-size: 1em;">
                Adquira a sua edição física ou em versão Kindle direto pela Amazon e comece a estruturar seus novos métodos hoje mesmo:
            </p>
            <a href="{link_afiliado}" target="_blank" rel="noopener noreferrer" style="display: inline-block; background-color: #ff9900; color: #111; font-weight: 700; text-decoration: none; padding: 14px 34px; border-radius: 6px; box-shadow: 0 3px 8px rgba(0,0,0,0.18); font-size: 1.05em;">
                Garantir Exemplar de "{t}" na Amazon
            </a>
        </div>

    </div>
    """
    return html

def publicar_no_blogger(titulo_post, conteudo_html):
    """Carrega o token de autenticação e insere o post diretamente via API."""
    if not BLOG_ID:
        raise ValueError("A variável BLOGGER_ID não está configurada.")

    raw_token = os.environ.get("BLOGGER_TOKEN_JSON")
    if not raw_token or not raw_token.strip():
        raise ValueError("O secret BLOGGER_TOKEN_JSON está vazio ou ausente!")

    token_info = json.loads(raw_token)
    creds = Credentials.from_authorized_user_info(token_info)

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

    service = build("blogger", "v3", credentials=creds)

    corpo = {
        "kind": "blogger#post",
        "title": titulo_post,
        "content": conteudo_html,
        "labels": ["Resenha", "Desenvolvimento Pessoal", "Livros", "Produtividade"]
    }

    post = service.posts().insert(blogId=BLOG_ID, body=corpo, isDraft=False).execute()
    print(f"\nArtigo publicado com sucesso!\nURL: {post.get('url')}")

def executar():
    livro = random.choice(LIVROS_CATALOGO)
    print(f"Gerando análise detalhada de: {livro['titulo']}...")

    capa_url, isbn, _ = obter_capa_livro(livro["titulo"], livro["autor"], livro.get("capa_manual", ""))
    fotos_pexels = obter_multiplas_fotos_pexels(livro.get("termos_pexels", []))
    link_amazon = gerar_link_amazon(livro["titulo"], livro["autor"], isbn)

    titulo_post = f"Análise Crítica: As Lições Ocultas em '{livro['titulo']}' ({livro['autor']})"
    html = gerar_artigo_completo(livro, capa_url, fotos_pexels, link_amazon)

    publicar_no_blogger(titulo_post, html)

if __name__ == "__main__":
    executar()

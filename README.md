# ZPrompt - Generador de Prompts para GLM

Genera prompts estructurados para desarrollo de software optimizados para GLM, usando OpenAI para la generacion inteligente.

## Stack

- **Backend**: FastAPI (Python)
- **Frontend**: HTML + Tailwind CSS v4 + JavaScript
- **AI**: OpenAI API (gpt-5.1-mini)
- **Deploy**: Vercel (Serverless Functions - Python Runtime)

## Estructura

```
main.py                  # FastAPI entry point
services/
  templates.py           # 5 templates de prompt
  openai_service.py      # Integracion OpenAI
public/
  index.html             # SPA frontend
  css/styles.css         # Tailwind compilado
  js/app.js              # Logica frontend
src/input.css            # Tailwind v4 source
vercel.json              # Routing config
```

## Tipos de Prompt

| Tipo | Descripcion |
|---|---|
| 🖥️ System | Rol y comportamiento del asistente AI |
| 🚀 Start | Inicializar proyecto nuevo |
| 🔄 Follow-Up | Agregar funcionalidad a proyecto existente |
| 🔍 Research | Investigar con Context7 antes de implementar |
| 🐛 Debug | Diagnosticar y resolver errores |

## Desarrollo Local

### Requisitos

- Python 3.12+
- Node.js 18+ (solo para compilar CSS)

### Setup

```bash
# 1. Instalar dependencias Python
pip install -r requirements.txt

# 2. Instalar dependencias Node (para Tailwind)
npm install

# 3. Compilar CSS
npm run build:css

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tu OPENAI_API_KEY

# 5. Ejecutar localmente
# Opcion A: con uvicorn
uvicorn main:app --reload --port 3000

# Opcion B: con Vercel CLI
npm i -g vercel
vercel dev
```

Abrir: `http://localhost:3000`

## Variables de Entorno

| Variable | Requerida | Descripcion |
|---|---|---|
| `OPENAI_API_KEY` | Si | API key de OpenAI |

## Deploy en Vercel

### 1. Push a GitHub

```bash
git init
git add .
git commit -m "Initial commit: ZPrompt"
git remote add origin <tu-repo>
git push -u origin main
```

### 2. Deploy

1. Ir a [vercel.com/new](https://vercel.com/new)
2. Conectar el repositorio
3. Vercel detectara automaticamente FastAPI
4. En **Settings > Environment Variables**, agregar:
   - `OPENAI_API_KEY` = tu API key de OpenAI
5. Click **Deploy**

### 3. Compilar CSS (si se modifica)

```bash
npm run build:css
git add public/css/styles.css
git commit -m "Update compiled CSS"
git push
```

## API Endpoints

| Metodo | Ruta | Descripcion |
|---|---|---|
| `GET` | `/` | SPA frontend |
| `GET` | `/api/health` | Health check |
| `GET` | `/api/templates` | Lista de tipos de prompt |
| `POST` | `/api/generate` | Generar prompt |
| `GET` | `/docs` | Swagger UI |

### POST /api/generate

Request:
```json
{
  "text": "Crear una API REST con Python...",
  "prompt_type": "system",
  "language": "Python",
  "framework": "FastAPI"
}
```

Response:
```json
{
  "prompt": "## 🖥️ SYSTEM PROMPT...",
  "prompt_type": "system",
  "label": "🖥️ System Prompt",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

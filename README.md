# Detección de Cloudflare en sitios web

## Contenido

- ¿Qué hace el script?
- Requisitos e instalación
- Formato de `websites.json` (ejemplos)
- Ejecutar el script
- Interpretación de resultados / ejemplo de salida
- Personalizaciones útiles (rango IP Cloudflare, detección)
- Troubleshooting rápido
- Licencia / contribuciones

---

## ¿Qué hace el script?

1. Lee `websites.json` (array de dominios).
2. Por cada dominio:

   - Resuelve la IP mediante DNS (`socket.gethostbyname`).
   - Realiza una petición `HEAD` a `https://{domain}` y examina headers para detectar indicios de Cloudflare (`Server`, `CF-RAY`, `CF-Cache-Status`).
   - Resalta si la IP empieza por un prefijo específico (`188.114.9` en la versión actual) — configurable.

3. Imprime por consola resultados coloreados y un resumen final con lista de dominios que usan Cloudflare y su IP.

---

## Requisitos e instalación

- Python 3.8+ (recomendado)

- Dependencias:

  ```bash
  pip install requests colorama beautifulsoup4
  ```

  _(beautifulsoup4 solo si usas variantes que parseen HTML; el script base necesita `requests` y `colorama`)_

- Nombre sugerido del archivo del script: `check_cloudflare.py`

- Coloca `websites.json` en el **mismo directorio** que el script.

---

## Formato de `websites.json`

**Reglas importantes:**

- Debe ser un **array JSON** de **strings**.
- Cada entrada **no** debe llevar `http://` ni `https://`.
- No hace falta la barra final `/`.
- Acepta dominios con `www` o sin `www` (se recomienda incluir la forma que quieras comprobar).
- Minúsculas recomendadas pero no obligatorio.

### Ejemplo mínimo (`websites.json`)

```json
["www.xataka.com", "xataka.com", "chollometro.com", "www.20minutos.es"]
```

### Ejemplo con muchos dominios

```json
[
  "www.chollometro.com",
  "www.miravia.es",
  "es.aliexpress.com",
  "www.tradedoubler.com",
  "michollo.com",
  "www.20minutos.es",
  "www.ahorradoras.com"
]
```

> ❗ Si metes por error `https://` al inicio, el script funcionará peor (está diseñado para añadir el `https://` internamente cuando hace la petición). Evita ese prefijo en el JSON.

---

## Ejecutar el script

Desde la carpeta con `check_cloudflare.py` y `websites.json`:

```bash
python3 check_cloudflare.py
```

Salida esperada (ejemplo):

```
[+] www.chollometro.com usa Cloudflare | IP: 104.21.33.XX
[-] www.miravia.es no parece usar Cloudflare | IP: 151.101.1.XX
[-] es.aliexpress.com no parece usar Cloudflare | IP: No disponible
[+] michollo.com usa Cloudflare | IP: 172.67.200.XX
...
Resumen: webs que usan Cloudflare:
www.chollometro.com | IP: 104.21.33.XX
michollo.com        | IP: 172.67.200.XX
```

Los colores:

- Verde → detectado Cloudflare
- Rojo → no detectado Cloudflare
- Amarillo → IP dentro del rango marcado (por defecto `188.114.9`)

---

## Personalizaciones y notas técnicas

### Detección de Cloudflare

El script comprueba headers `Server`, `CF-RAY`, `CF-Cache-Status`. Esto cubre la mayoría de casos, pero no es 100% infalible (sitios pueden ocultar headers). Si quieres reforzar la detección, añade otros checks, por ejemplo:

- Buscar `cloudflare` en `Server` (como ya hace).
- Comprobar cabeceras `via` o `x-served-by`.
- Hacer una petición `GET` y revisar cookies (`__cfduid` histórico).

### Rango IP Cloudflare

- En el script verás la función `is_cf_ip(ip)` que actualmente hace `ip.startswith("188.114.9")`.
- **Mejor práctica**: usar la lista oficial de rangos de Cloudflare (actualizada) en [https://www.cloudflare.com/ips/](https://www.cloudflare.com/ips/) y comprobar si la IP consultada pertenece a alguno de esos prefijos. Ejemplo simple para múltiples prefijos:

```python
CF_RANGES = ["173.245.48.0/20", "103.21.244.0/22", ...]  # obtener desde cloudflare.com/ips

# Puedes usar ipaddress para comprobar pertenencia:
import ipaddress
def ip_in_ranges(ip, ranges):
    ip_obj = ipaddress.ip_address(ip)
    for r in ranges:
        if ip_obj in ipaddress.ip_network(r):
            return True
    return False
```

### Obtener IP real del servidor (fuera de Cloudflare)

Si la IP pertenece a Cloudflare, la IP DNS es la del proxy y **no** la IP real del servidor de origen. Para obtener la IP real necesitas acceso al servidor, registros DNS previos, o datos del proveedor.

---

## Troubleshooting rápido

- `"No disponible"` en IP:

  - DNS falla o tu máquina no resuelve el nombre.
  - Dominio inválido en `websites.json`.

- `requests.head` falla / timeout:

  - Conexión bloqueada, certificado TLS extraño, o el servidor no responde a `HEAD`. Puedes cambiar a `requests.get(..., stream=True)` si `HEAD` falla en algunos hosts.

- Resultado combinado/URL concatenada:

  - Revisa el `websites.json`: cuidado con comas faltantes o strings concatenados.

---

## Seguridad y privacidad

- El script realiza peticiones HTTPS púbicas y hace resolución DNS; no guarda ni comparte los datos.
- Si lo usas contra hosts que no controlas, respeta las políticas de uso y no abuses de peticiones repetidas.

---

## Contribuciones y licencia

- Licencia: MIT (usa libremente, atribución opcional).

---

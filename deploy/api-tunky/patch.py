# Registra el módulo cien.js en /opt/api-tunky/src/server.js (idempotente). Lo ejecuta deploy.sh en el VPS.
# Se engancha DESPUÉS de la línea de makePais si existe; si no, después de makeCounter (la misma ancla que usa Agenda País).
p = "/opt/api-tunky/src/server.js"
s = open(p).read()
if 'require("./cien")' in s:
    print("ya estaba")
else:
    anclas = [
        'Object.assign(routes, makePais({ DATA_DIR, json, clean, readBody }));\n',
        'Object.assign(routes, makeCounter({ DATA_DIR, json, clean, readBody }));\n',
    ]
    ancla = next((a for a in anclas if a in s), None)
    assert ancla, "ancla no encontrada: revisa server.js a mano"
    s = s.replace(ancla, ancla + 'const makeCien = require("./cien");\nObject.assign(routes, makeCien({ DATA_DIR, json, clean, readBody }));\n', 1)
    open(p, "w").write(s)
    print("parcheado")

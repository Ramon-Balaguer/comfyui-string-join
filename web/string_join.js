import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

const DEBUG_SETTING_ID = "StringJoin.DebugLogs";

// Envía al servidor si los logs de debug están activados (se imprimen en la consola de ComfyUI).
function sendDebugFlag(enabled) {
  api.fetchApi("/string_join/debug", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ enabled: !!enabled }),
  }).catch((err) => console.warn("[StringJoin] no se pudo cambiar el debug:", err));
}

app.registerExtension({
  name: "comfyui-string-join.debug-setting",
  settings: [
    {
      id: DEBUG_SETTING_ID,
      name: "Mostrar logs de debug en la consola del servidor",
      type: "boolean",
      defaultValue: false,
      category: ["String Join", "Debug", "Logs de debug"],
      onChange: (value) => sendDebugFlag(value),
    },
  ],
  async setup() {
    // Sincroniza el valor guardado al cargar la página (el servidor arranca con debug desactivado).
    sendDebugFlag(app.ui.settings.getSettingValue(DEBUG_SETTING_ID, false));
  },
});

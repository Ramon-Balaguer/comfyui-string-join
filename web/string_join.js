import { app } from "../../scripts/app.js";

const NODE_NAME = "StringJoinMulti";

// Botón "Reset inputs": desconecta todos los strings y restaura los widgets a sus valores por defecto.
app.registerExtension({
  name: "comfyui-string-join.reset-inputs",
  async beforeRegisterNodeDef(nodeType, nodeData) {
    if (nodeData.name !== NODE_NAME) return;

    const defaults = {};
    for (const group of ["required", "optional"]) {
      for (const [name, spec] of Object.entries(nodeData.input?.[group] ?? {})) {
        if (spec?.[1]?.default !== undefined) defaults[name] = spec[1].default;
      }
    }

    const onNodeCreated = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function () {
      const result = onNodeCreated?.apply(this, arguments);
      this.addWidget("button", "Reset inputs", null, () => {
        for (let i = this.inputs.length - 1; i >= 0; i--) {
          if (this.inputs[i].link != null) this.disconnectInput(i);
        }
        for (const widget of this.widgets) {
          if (widget.type !== "button" && widget.name in defaults) widget.value = defaults[widget.name];
        }
        this.setDirtyCanvas(true, true);
      });
      return result;
    };
  },
});

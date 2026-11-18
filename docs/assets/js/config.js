/* =========================================================
   CONFIGURACIÓN EDITABLE — CrediPensión
   Cambia aquí las tasas y el número de WhatsApp.
   Todo el sitio (simulador y tabla de tarifas) se actualiza solo.
   ========================================================= */
window.CP_CONFIG = {
  // Número de WhatsApp (código de país + número, sin espacios ni "+")
  whatsapp: "573108038677",

  // Tasas de referencia (Nominal Mes Vencido, en %)
  tasaMinNMV: 1.45,
  tasaMaxNMV: 1.81,

  // Tasas Efectivas Anuales que se muestran en la tabla (en %)
  tasaMinEA: 18.86,
  tasaMaxEA: 24.02,

  // Seguro de vida mensual por cada millón prestado (COP)
  seguroVidaPorMillon: 4625,

  // Plazos (meses)
  plazoMin: 12,
  plazoMax: 144,

  // Límites del simulador (COP)
  montoMin: 1000000,
  montoMax: 150000000,
  montoInicial: 20000000,
  cuotaMin: 100000,
  cuotaMax: 3000000,
  cuotaInicial: 400000,

  // Fecha de actualización que se muestra junto a las tarifas
  actualizado: "julio de 2026"
};

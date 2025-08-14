const paramsContainer = document.getElementById('paramsContainer');
const resultBox = document.getElementById('resultBox');
const resultSection = document.getElementById('result');
const form = document.getElementById('recoForm');
const categorySel = document.getElementById('categorySel');

const PARAMS_BY_CATEGORY = {
  "Die Lube": [
    "Existing grade Name","Existing Supplier Name","Consumption per Day/Month","DRA Sample Collected",
    "Dilution Ratio","Tank","Tank Cleaning Period","Tank Capacity (Mixing)","Tank Capacity (Holding)",
    "Spray System","Spray Time","Water Type","Air Blow Time","Water Quality - TDS (ppm)",
    "Water Quality - Hardness (ppm)","Water Quality - pH Value (ppm)","Air Type"
  ],
  "Granular Flux": [
    "Furnace Capacity (Melting)","Furnace Capacity (Holding)","Furnace Type","Melting Per Day/Month","Aluminium Grade",
    "Existing Grade","Metal Temperature (Melting)","Metal Temperature (Holding)","Type of Degassing Method","Degassing Equipment Name",
    "Rotor Speed","Dose of Granular/Powder/Tablet in Kgs","Consumption and Price Per Kgs"
  ],
  "Powder Flux": [
    "Furnace Capacity (Melting)","Furnace Capacity (Holding)","Furnace Type","Melting Per Day/Month","Aluminium Grade",
    "Existing Grade","Metal Temperature (Melting)","Metal Temperature (Holding)","Type of Degassing Method","Degassing Equipment Name",
    "Rotor Speed","Dose of Granular/Powder/Tablet in Kgs","Consumption and Price Per Kgs"
  ],
  "Forging Lube": [
    "Forging (Component) Part Name","Weight of the Part in Kgs","Component Type","Complexity of Part","Billet Temp Range","Die Temp",
    "Existing Lube Grade Name","Existing Supplier Name","Dilution Ratio","Consumption of Lube Per Ton","Die Life","Additional Lube in Use","Any Additional Improvement Required"
  ],
  "Ladle Coat": [
    "Ladle Coat Supplier Name","Ladle coat Grade Name","Type of Coating for cup","Material of Pouring Cup","Metal Temperature (Holding)","No. of Dips"
  ],
  "Plunger Lube": [
    "Piston Diameter","Supplier Name","Type of Lubrication","Where To apply","Dose Per Shot","Consumption per Month","Life of previous Plunger Tip"
  ]
};

function renderParams(category){
  paramsContainer.innerHTML = "";
  const keys = PARAMS_BY_CATEGORY[category];
  if(!keys){ return; }
  const fs = document.createElement('fieldset');
  const legend = document.createElement('legend');
  legend.textContent = category + " Parameters";
  fs.appendChild(legend);
  const grid = document.createElement('div');
  grid.className = "smallgrid";
  keys.forEach(k => {
    const w = document.createElement('label');
    w.textContent = k;
    const inp = document.createElement(k.toLowerCase().includes("details") ? "textarea" : "input");
    inp.name = "param__" + k;
    grid.appendChild(w);
    w.appendChild(inp);
  });
  fs.appendChild(grid);
  paramsContainer.appendChild(fs);
}

categorySel.addEventListener('change', (e)=>{
  renderParams(e.target.value);
});

form.addEventListener('submit', async (e)=>{
  e.preventDefault();
  const fd = new FormData(form);
  const payload = {
    division: fd.get('division'),
    category: fd.get('category'),
    requirement_type: fd.get('requirement_type'),
    priority: fd.get('priority'),
    customer_name: fd.get('customer_name'),
    requirement_details: fd.get('requirement_details'),
    params: {}
  };
  for (const [k,v] of fd.entries()) {
    if(k.startsWith('param__')){
      payload.params[k.replace('param__','')] = v;
    }
  }
  resultSection.classList.remove('hidden');
  resultBox.textContent = "Analyzing...";
  try{
    const res = await fetch('/api/recommend', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify(payload)
    });
    const j = await res.json();
    resultBox.textContent = JSON.stringify(j, null, 2);
  }catch(err){
    resultBox.textContent = "Error: " + err.message;
  }
});

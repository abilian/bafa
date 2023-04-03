function makeChart(opts, data) {
  const element = document.getElementById("plots");
  new uPlot(opts, data, element);
}

fetch("/data.json")
    .then((r) => r.json())
    .then((json) => {
      // console.log(json);
      for (let i = 0; i < json.length; i++) {
        console.log(JSON.stringify(json[i]));
        const opts = json[i].opts;
        const data = json[i].data;
        makeChart(opts, data)
        // break;
      }
    });

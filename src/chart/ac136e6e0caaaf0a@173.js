// https://observablehq.com/@laurentmau/chart-template@173
import define1 from "./e93997d5089d7165@2283.js";

export default function define(runtime, observer) {
  const main = runtime.module();
  main.variable(observer()).define(["md"], function(md){return(
md`# 5R Calculator `
)});
  main.variable(observer("impact")).define("impact", ["i"], function(i){return(
i
)});
  main.variable(observer("faisabilite")).define("faisabilite", ["f"], function(f){return(
f
)});
  main.variable(observer("viewof reseau1")).define("viewof reseau1", ["slider"], function(slider){return(
slider({
  min: 0, 
  max: 5, 
  step: 1, 
  value: 5, 
  title: "Capacité du réseau à répondre au besoin", 
  description: "1- Faible 5- Forte"
})
)});
  main.variable(observer("reseau1")).define("reseau1", ["Generators", "viewof reseau1"], (G, _) => G.input(_));
  main.variable(observer("viewof f")).define("viewof f", ["slider"], function(slider){return(
slider({
  min: 0, 
  max: 100, 
  step: 1, 
  value: 100, 
  title: "faisabilité", 
  description: "1- Faible 5- Forte"
})
)});
  main.variable(observer("f")).define("f", ["Generators", "viewof f"], (G, _) => G.input(_));
  main.variable(observer("viewof i")).define("viewof i", ["slider"], function(slider){return(
slider({
  min: 0, 
  max: 100, 
  step: 1, 
  value: 100, 
  title: "impact", 
  description: "1- Faible 5- Forte"
})
)});
  main.variable(observer("i")).define("i", ["Generators", "viewof i"], (G, _) => G.input(_));
  main.variable(observer("chart5R")).define("chart5R", ["d3","width","height","xAxis","yAxis","x","y","impact","faisabilite"], function(d3,width,height,xAxis,yAxis,x,y,impact,faisabilite)
{
  
  const svg = d3.create("svg")
      .attr("viewBox", [0, 0, width, height]);

  svg.append("g")
      .call(xAxis);

  svg.append("g")
      .call(yAxis);
  svg.append("g")
  .append('circle')
    .attr('cx', x(50))
    .attr('cy', y(50))
    .attr('r', 20)
    .style('fill', 'green');
   svg.append("rect")
      .attr("x", x(66))
      .attr("y", y(100))
      .attr("width", x(34)-x(0))
      .attr("height", (y(0)-y(33)))
       .attr ("fill", "#EEFDE5");
  svg.append("rect")
      .attr("x", x(50))
      .attr("y", y(100))
      .attr("width", x(17)-x(0))
      .attr("height", y(0)-y(50))
      .attr ("fill", "#f2d387");
    svg.append("rect")
      .attr("x", x(50))
      .attr("y", y(67))
      .attr("width", x(50)-x(0))
      .attr("height", y(0)-y(17))
      .attr ("fill", "#f2d387");
  svg.append("rect")
      .attr("x", x(0))
      .attr("y", y(100))
      .attr("width", x(50)-x(0))
      .attr("height", y(0)-y(100))
      .attr ("fill", "#f9b6b6");
    svg.append("rect")
      .attr("x", x(0))
      .attr("y", y(50))
      .attr("width", x(100)-x(0))
      .attr("height", y(0)-y(50))
      .attr ("fill", "#f9b6b6");
  svg.append("g")
  .append('circle')
    .attr('cx', x(impact))
    .attr('cy', y(faisabilite))
    .attr('r', 5)
    .style('fill', 'gray');

  return svg.node();
}
);
  main.variable(observer("path")).define("path", ["shape2path"], function(shape2path){return(
shape2path.rect()
  .attr("x", d => d.x)
  .attr("y", d => d.y)
  .attr("width", d => d.w)
  .attr("height", d => d.h)
  .attr("rx", d => d.rx)
  .attr("ry", d => d.ry)
)});
  main.variable(observer("x")).define("x", ["d3","margin","width"], function(d3,margin,width){return(
d3.scaleLinear()
    .domain([0, 100])
    .range([margin.left, width - margin.right])
)});
  main.variable(observer("y")).define("y", ["d3","height","margin"], function(d3,height,margin){return(
d3.scaleLinear()
    .domain([0, 100])
    .range([height - margin.bottom, margin.top])
)});
  main.variable(observer("xAxis")).define("xAxis", ["height","margin","d3","x"], function(height,margin,d3,x){return(
g => g
    .attr("transform", `translate(0,${height - margin.bottom})`)
    .call(d3.axisBottom(x))
)});
  main.variable(observer("yAxis")).define("yAxis", ["margin","d3","y"], function(margin,d3,y){return(
g => g
    .attr("transform", `translate(${margin.left},0)`)
    .call(d3.axisLeft(y))
)});
  main.variable(observer("margin")).define("margin", function(){return(
{top: 20, right: 30, bottom: 30, left: 40}
)});
  main.variable(observer("height")).define("height", ["width"], function(width){return(
width
)});
  main.variable(observer("d3")).define("d3", ["require"], function(require){return(
require("d3@5")
)});
  main.variable(observer("shape2path")).define("shape2path", ["require"], function(require){return(
require("shape2path@3.0.3")
)});
  const child1 = runtime.module(define1);
  main.import("input", child1);
  const child2 = runtime.module(define1);
  main.import("slider", child2);
  return main;
}

const data = {
  mainPaper: {
    title: "MACRec: A Multi-Agent Collaboration Framework for Recommendation",
    citationCount: 4,
    year: 2024
  },
  citedPapers: [
    { title: "[1] Language models are few-shot learners", citationCount: 38863, year: 2020 },
    { title: "[3] Agentverse: Facilitating multi-agent collaboration and exploring emergent behaviors in agents", citationCount: 155, year: 2023 },
    { title: "[4] Improving Factuality and Reasoning in Language Models through Multiagent Debate", citationCount: 437, year: 2023 },
    { title: "[6] Camel: Communicative agents for 'mind' exploration of large scale language model society", citationCount: 523, year: 2023 },
    { title: "[7] Webgpt: Browser-assisted question-answering with human feedback", citationCount: 1100, year: 2021 },
    { title: "[9] GPT-4 Technical Report", citationCount: 7299, year: 2023 },
    { title: "[10] Hugginggpt: Solving ai tasks with chatgpt and its friends in huggingface", citationCount: 1016, year: 2023 }
  ]
};

let svg, simulation, nodes, links;

const width = window.innerWidth;
const height = window.innerHeight;

function createGraph() {
  svg = d3.select("body")
    .append("svg")
    .attr("width", width)
    .attr("height", height);

  simulation = d3.forceSimulation()
    .force("link", d3.forceLink().id(d => d.id).distance(200))
    .force("charge", d3.forceManyBody().strength(-300))
    .force("center", d3.forceCenter(width / 2, height / 2))
    .force("x", d3.forceX(width / 2).strength(0.1))
    .force("y", d3.forceY(height / 2).strength(0.1));

  nodes = [
    {
      id: data.mainPaper.title,
      size: Math.max(20, Math.log(data.mainPaper.citationCount + 1) * 15),
      citationCount: data.mainPaper.citationCount,
      year: data.mainPaper.year
    }
  ];

  links = [];

  data.citedPapers.forEach(paper => {
    nodes.push({
      id: paper.title,
      size: Math.max(20, Math.log(paper.citationCount + 1) * 15),
      citationCount: paper.citationCount,
      year: paper.year
    });
    links.push({ source: data.mainPaper.title, target: paper.title });
  });

  svg.append("defs").append("marker")
    .attr("id", "arrow")
    .attr("viewBox", "0 -5 10 10")
    .attr("refX", 10)
    .attr("refY", 0)
    .attr("markerWidth", 6)
    .attr("markerHeight", 6)
    .attr("orient", "auto")
    .append("path")
    .attr("d", "M0,-5L10,0L0,5")
    .attr("fill", "#aaa");

  const link = svg.append("g")
    .attr("class", "links")
    .selectAll("line")
    .data(links)
    .enter()
    .append("line")
    .attr("stroke", "#aaa")
    .attr("stroke-width", 1.5)
    .attr("marker-end", "url(#arrow)");

  // ⬇⬇⬇ 원과 텍스트를 같은 <g> 그룹 내에 추가 ⬇⬇⬇
  const nodeGroup = svg.append("g")
    .attr("class", "nodes")
    .selectAll("g")
    .data(nodes)
    .enter()
    .append("g")
    .attr("class", "node");

  nodeGroup.append("circle")
    .attr("r", d => d.size)
    .attr("fill", "skyblue")
    .attr("stroke", "#333")
    .attr("stroke-width", 1.5)
    .on("mouseover", function () {
      d3.select(this).attr("fill", "#ff4500");
    })
    .on("mouseout", function () {
      d3.select(this).attr("fill", "skyblue");
    })
    .call(d3.drag()
      .on("start", dragstarted)
      .on("drag", dragged)
      .on("end", dragended));

  nodeGroup.append("text")
    .text(d => `${d.citationCount.toLocaleString()}`)
    .attr("fill", "white")
    .attr("font-size", d => Math.max(10, d.size / 3))
    .attr("text-anchor", "middle")
    .attr("dy", d => d.size / 10);

  simulation
    .nodes(nodes)
    .on("tick", () => {
      link
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y);

      nodeGroup.attr("transform", d => `translate(${d.x}, ${d.y})`);
    });

  simulation.force("link").links(links);
}

function dragstarted(event) {
  if (!event.active) {
    simulation.alphaTarget(0.3).restart()
  }
  event.subject.fx = event.subject.x;
  event.subject.fy = event.subject.y
}

function dragged(event) {
  event.subject.fx = event.x;
  event.subject.fy = event.y
}

function dragended() {
  if (!event.active) {
    simulation.alphaTarget(0)
  }

  event.subject.fx = null;
  event.subject.fy = null
}

function sortByValue() {
  nodes.sort((a, b) => b.citationCount - a.citationCount);

  nodes.forEach((node, i) => {
    node.fx = (width / (nodes.length + 1)) * (i + 1);
    node.fy = height / 2;
  });

  simulation.alpha(1).restart();
}

createGraph();

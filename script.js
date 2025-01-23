const data = {
    mainPaper: {
      title: "MACRec: A Multi-Agent Collaboration Framework for Recommendation",
      citationCount: 4,
      year: 2024
    },
    citedPapers: [
      { title: "Language models are few-shot learners", citationCount: 38863, year: 2020 },
      { title: "Agentverse: Facilitating multi-agent collaboration and exploring emergent behaviors in agents", citationCount: 155, year: 2023 },
      { title: "Improving Factuality and Reasoning in Language Models through Multiagent Debate", citationCount: 437, year: 2023 },
      { title: "Camel: Communicative agents for 'mind' exploration of large scale language model society", citationCount: 523, year: 2023 },
      { title: "Webgpt: Browser-assisted question-answering with human feedback", citationCount: 1100, year: 2021 },
      { title: "GPT-4 Technical Report", citationCount: 7299, year: 2023 },
      { title: "Hugginggpt: Solving ai tasks with chatgpt and its friends in huggingface", citationCount: 1016, year: 2023 }
    ]
  };

//   let으로 선언된 변수는 해당 블록 내에서만 사용가능
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

    const node = svg.append("g")
      .attr("class", "nodes")
      .selectAll("circle")
      .data(nodes)
      .enter()
      .append("circle")
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

    svg.append("g")
      .attr("class", "labels")
      .selectAll("text")
      .data(nodes)
      .enter()
      .append("text")
      .text(d => `${d.citationCount.toLocaleString()}`)
      .attr("font-size", 14)
      .attr("dx", 0)
      .attr("dy", 4)
      .attr("text-anchor", "middle");

    svg.append("g")
      .attr("class", "year-labels")
      .selectAll("text")
      .data(nodes.filter(d => d.year))
      .enter()
      .append("text")
      .text(d => d.year)
      .attr("class", "year-label")
      .attr("x", (d, i) => width / (nodes.length + 1) * (i + 1))
      .attr("y", height - 20);

    simulation
      .nodes(nodes)
      .on("tick", () => {
        link
          .attr("x1", d => d.source.x)
          .attr("y1", d => d.source.y)
          .attr("x2", d => d.target.x)
          .attr("y2", d => d.target.y);

        node
          .attr("cx", d => d.x)
          .attr("cy", d => d.y);

        svg.selectAll(".labels text")
          .attr("x", d => d.x)
          .attr("y", d => d.y);
      });

    simulation.force("link").links(links);
  }

  function dragstarted(event, d) {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
  }

  function dragged(event, d) {
    d.fx = event.x;
    d.fy = event.y;
  }

  function dragended(event, d) {
    if (!event.active) simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
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
const width = Math.max(document.documentElement.clientWidth, window.innerWidth || 0);
const height = Math.max(document.documentElement.clientHeight, window.innerHeight || 0);

console.log(width)
console.log(height)
const papersElement = document.getElementById("papers-data");
const papersJSON = papersElement.textContent;
const papers = JSON.parse(papersJSON);

svg = d3.select("body")
  .append("svg")
  .attr("width", width)
  .attr("height", height);

data = {
  mainPaper: {
    title: "MACRec: A Multi-Agent Collaboration Framework for Recommendation",
    citationCount: 4,
    year: 2024
  },
  citedPapers: papers.map(paper => ({
    title: `[${paper.id}] ${paper.title}`,
    citationCount: paper.citationCount,
    year: paper.year
  }))
};

nodes = [
  {
    id: data.mainPaper.title,
    size: Math.max(10, Math.log(data.mainPaper.citationCount + 1) * 10),
    citationCount: data.mainPaper.citationCount,
    year: data.mainPaper.year
  }
];

links = [];

data.citedPapers.forEach(paper => {
  nodes.push({
    id: paper.title,
    size: Math.max(10, Math.log(paper.citationCount + 1) * 6),
    citationCount: paper.citationCount,
    year: paper.year
  });
});

console.log("nodes", nodes)

const radiusScale = d3.scaleSqrt()
  .domain([d3.min(nodes, d => d.citationCount), d3.max(nodes, d => d.citationCount)])
  .range([20, 80]);

// createGraph();
console.log("data", data)
console.log("nodes", nodes)

let circle_tags = svg.selectAll("circle")
  .data(nodes)
  .enter()
  .append("circle")
  .attr("r", d => radiusScale(d.citationCount) + 5)
  .attr("fill", "skyblue")
  .attr("stroke", "#333")
  .attr("stroke-width", 1.5)
  .on("mouseover", function (event, d) {
    d3.select(this).attr("fill", "#ff4500");

    title_texts
      .filter(textData => textData.id === d.id)
      .attr("opacity", "1"); // 제목의 투명도를 1로 변경
  })
  .on("mouseout", function (event, d) {
    d3.select(this).attr("fill", "skyblue");

    title_texts
      .filter(textData => textData.id === d.id)
      .attr("opacity", "0.3"); // 다시 원래대로 투명도 조정
  })
  .call(d3.drag()
    .on("start", dragStarted)
    .on("drag", dragged)
    .on("end", dragEnded)
  );

  let title_texts = svg.selectAll(".title-text")  // ✅ 클래스 추가
  .data(nodes)
  .enter()
  .append("text")
  .classed("title-text", true)  // ✅ 클래스 부여
  .text(d => d.id)
  .attr("dx", d => d.size / 10)
  .attr("opacity", "0.2");

  let citation_count_texts = svg.selectAll(".citation-text")  // ✅ 다른 클래스 사용
  .data(nodes)
  .enter()
  .append("text")
  .classed("citation-text", true)  // ✅ 클래스 부여
  .text(d => `${d.citationCount.toLocaleString()}`)
  .attr("fill", "white")
  .attr("font-size", d => Math.max(8, d.size / 3))
  .attr("text-anchor", "middle")
  .attr("dy", d => d.size / 20);; // 크기를 원 크기에 비례하게 설정


const simulation = d3.forceSimulation(nodes)
  .force("charge", d3.forceManyBody().strength(0))
  .force("center", d3.forceCenter(width / 2, height / 2))
  .force("collision", d3.forceCollide(d => radiusScale(d.citationCount) + 5))
  .on("tick", ticked);

  function ticked() {
    circle_tags
        .attr("cx", d => d.x || Math.random() * width)  // ✅ 수정 (NaN 방지)
        .attr("cy", d => d.y || Math.random() * height);  // ✅ 수정 (NaN 방지)

    title_texts
        .attr("x", d => d.x || Math.random() * width)  // ✅ 수정 (NaN 방지)
        .attr("y", d => (d.y || Math.random() * height) + 20);  // ✅ 수정 (NaN 방지)

    citation_count_texts
        .attr("x", d => d.x || Math.random() * width)  // ✅ 수정 (NaN 방지)
        .attr("y", d => (d.y || Math.random() * height) + 4);  // ✅ 수정 (NaN 방지)
}


function dragStarted(event, d) {
  if (!event.active) simulation.alphaTarget(0.3).restart();
  d.fx = d.x;
  d.fy = d.y;
}

function dragged(event, d) {
  d.fx = event.x;
  d.fy = event.y;
}

function dragEnded(event, d) {
  if (!event.active) simulation.alphaTarget(0);
  d.fx = d.x;
  d.fy = d.y;
}

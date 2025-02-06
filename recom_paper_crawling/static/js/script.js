// const data = {
//   mainPaper: {
//     title: "MACRec: A Multi-Agent Collaboration Framework for Recommendation",
//     citationCount: 4,
//     year: 2024
//   },
//   citedPapers: [
//     { title: "[1] Language models are few-shot learners", citationCount: 38863, year: 2020 },
//     { title: "[3] Agentverse: Facilitating multi-agent collaboration and exploring emergent behaviors in agents", citationCount: 155, year: 2023 },
//     { title: "[4] Improving Factuality and Reasoning in Language Models through Multiagent Debate", citationCount: 437, year: 2023 },
//     { title: "[6] Camel: Communicative agents for 'mind' exploration of large scale language model society", citationCount: 523, year: 2023 },
//     { title: "[7] Webgpt: Browser-assisted question-answering with human feedback", citationCount: 1100, year: 2021 },
//     { title: "[9] GPT-4 Technical Report", citationCount: 7299, year: 2023 },
//     { title: "[10] Hugginggpt: Solving ai tasks with chatgpt and its friends in huggingface", citationCount: 1016, year: 2023 }
//   ]
// };


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

const circle_tags = svg.selectAll("circle")
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

const title_texts = svg.selectAll(".title-text")  // ✅ 클래스 추가
  .data(nodes)
  .enter()
  .append("text")
  .classed("title-text", true)  // ✅ 클래스 부여
  .text(d => d.id)
  .attr("dx", d => d.size / 10)
  .attr("opacity", "0.2");

const citation_count_texts = svg.selectAll(".citation-text")  // ✅ 다른 클래스 사용
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
    .attr("cx", d => d.x)
    .attr("cy", d => d.y);

  title_texts
    .attr("x", d => d.x)
    .attr("y", d => d.y + 20);

  citation_count_texts
    .attr("x", d => d.x)
    .attr("y", d => d.y + 4);
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

// function createGraph() {
//   svg = d3.select("body")
//     .append("svg")
//     .attr("width", width)
//     .attr("height", height);

//   svg.append("defs").append("marker")
//     .attr("id", "arrow")
//     .attr("viewBox", "0 -5 10 10")
//     .attr("refX", 10)
//     .attr("refY", 0)
//     .attr("markerWidth", 6)
//     .attr("markerHeight", 6)
//     .attr("orient", "auto")
//     .append("path")
//     .attr("d", "M0,-5L10,0L0,5")
//     .attr("fill", "#aaa");

//   console.log("links : ", links)
//   const link = svg.append("g")
//     .attr("class", "links")
//     .selectAll("line")
//     .data(links)
//     .enter()
//     .append("line")
//     .attr("stroke", "#aaa")
//     .attr("stroke-width", 1.5)
//     .attr("marker-end", "url(#arrow)");
//   console.log("links : ", links)

//   // ⬇⬇⬇ 원과 텍스트를 같은 <g> 그룹 내에 추가 ⬇⬇⬇
//   // const nodeGroup = svg.append("g")
//   //   .attr("class", "nodes")
//   //   .selectAll("g")
//   //   .data(nodes)
//   //   .enter()
//   //   .append("g")
//   //   .attr("class", "node");

//   node.append("circle")
//     .attr("r", d => d.size)
//     .attr("fill", "skyblue")
//     .attr("stroke", "#333")
//     .attr("stroke-width", 1.5)
//     .on("mouseover", function () {
//       d3.select(this).attr("fill", "#ff4500");
//     })
//     .on("mouseout", function () {
//       d3.select(this).attr("fill", "skyblue");
//     })
//     .call(d3.drag()
//       .on("start", dragstarted)
//       .on("drag", dragged)
//       .on("end", dragended));

//   // nodeGroup.append("text")
//   //   .text(d => `${d.citationCount.toLocaleString()}`)
//   //   .attr("fill", "white")
//   //   .attr("font-size", d => Math.max(10, d.size / 3))
//   //   .attr("text-anchor", "middle")
//   //   .attr("dy", d => d.size / 10);

//   // 논문 제목 추가
//   // nodeGroup.append("text")
//   //   .text(d => d.id) // 논문 제목 표시
//   //   .attr("fill", "gray")
//   //   // .attr("font-size", d => Math.max(8, d.size / 5)) // 크기를 원 크기에 비례하게 설정
//   //   // .attr("text-anchor", "middle")
//   //   .attr("dx", d => d.size / 2)
//   //   .attr("dy", d => d.size / 10) // 제목을 인용 수 아래에 배치
//   //   .attr("class", "title-label")
//   // // .call(wrapText, 100); // 긴 제목을 자동 줄바꿈 (아래에 wrapText 함수 추가됨)

//   console.log("nodes", nodes)
//   simulation = d3.forceSimulation(nodes)
//     // .force("link", d3.forceLink().id(d => d.id).distance(300))
//     .force("charge", d3.forceManyBody().strength(5))
//     .force("center", d3.forceCenter(width / 2, height / 2))
//     .force("collision", d3.forceCollide(d => radiusScale(d.citations) + 5))
//     .on("tick", ticked);

//   // simulation.nodes(nodes)
//   //           .on("tick", () => {
//   //                               link.attr("x1", d => d.source.x)
//   //                                   .attr("y1", d => d.source.y)
//   //                                   .attr("x2", d => d.target.x)
//   //                                   .attr("y2", d => d.target.y);
//   //                               nodeGroup.attr("transform", d => `translate(${d.x}, ${d.y})`);
//   //                             }
//   //               );

//   // simulation.force("link").links(links);
//   console.log("Graph created successfully!"); // ✅ 디버깅용 로그 추가
// }

// function dragstarted(event) {
//   if (!event.active) {
//     simulation.alphaTarget(0.3).restart();
//   }
//   // event.subject.fx = event.subject.x;
//   // event.subject.fy = event.subject.y;

//   // ⬇⬇⬇ 드래그 발생 시 연도 라벨 제거 ⬇⬇⬇
//   // svg.select(".year-labels").remove();

// }

// function dragged(event) {
//   event.subject.fx = event.x;
//   event.subject.fy = event.y;

// }

// function dragended(event) {
//   if (!event.active) {
//     simulation.alphaTarget(0)
//   }

//   event.subject.fx = null;
//   event.subject.fy = null
// }

// function sortByYearAndCitation() {
//   // 1️⃣ 연도별로 그룹화
//   const yearGroups = {};
//   nodes.forEach(node => {
//     if (!yearGroups[node.year]) {
//       yearGroups[node.year] = [];
//     }
//     yearGroups[node.year].push(node);
//   });

//   // 2️⃣ 각 연도 그룹을 인용 수 기준으로 정렬
//   Object.keys(yearGroups).forEach(year => {
//     yearGroups[year].sort((a, b) => b.citationCount - a.citationCount);
//   });

//   // 3️⃣ 화면 너비를 연도 개수로 나누어 x 위치 결정
//   const uniqueYears = Object.keys(yearGroups).sort((a, b) => a - b); // 연도 오름차순 정렬
//   const yearSpacing = width / (uniqueYears.length + 1); // 연도별 x 간격
//   const verticalSpacing = 80; // 같은 연도 내 세로 간격

//   uniqueYears.forEach((year, yearIndex) => {
//     const yearNodes = yearGroups[year];
//     const centerX = yearSpacing * (yearIndex + 1); // 해당 연도의 X 위치

//     yearNodes.forEach((node, nodeIndex) => {
//       node.fx = centerX;
//       node.fy = height / 2 + nodeIndex * verticalSpacing - (yearNodes.length * verticalSpacing) / 2;
//     });
//   });

//   // 4️⃣ Force Simulation 다시 실행
//   // simulation.alpha(1).restart();

//   // 5️⃣ 연도를 화면 하단에 추가 (버튼을 눌렀을 때만 보이게)
//   svg.select(".year-labels").remove(); // 기존 연도 라벨 삭제

//   svg.append("g")
//     .attr("class", "year-labels")
//     .selectAll("text")
//     .data(uniqueYears)
//     .enter()
//     .append("text")
//     .text(d => d) // 연도 표시
//     .attr("x", (d, i) => yearSpacing * (i + 1))
//     .attr("y", height - 20)
//     .attr("text-anchor", "middle")
//     .attr("font-size", "16px")
//     .attr("fill", "black")
//     .style("opacity", 0) // 처음에는 숨김
//     .transition().duration(500) // 애니메이션 효과
//     .style("opacity", 1);
// }
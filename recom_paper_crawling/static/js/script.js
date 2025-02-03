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

let svg, simulation, nodes, links;

const width = Math.max(document.documentElement.clientWidth, window.innerWidth || 0);
const height = Math.max(document.documentElement.clientHeight, window.innerHeight || 0);

console.log(width)
console.log(height)

document.addEventListener("DOMContentLoaded", () => {

  // HTML의 <script id="papers-data">에서 JSON 데이터 가져오기
  const papersElement = document.getElementById("papers-data");

  if (!papersElement) {
    console.error("Error: 'papers-data' element not found.");
    return;
  }
  const papersJSON = papersElement.textContent;

  try {
    const papers = JSON.parse(papersJSON);

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
    createGraph();
  } catch (error) {
    console.error("Error parsing JSON:", error);
  }



});

function createGraph() {
  svg = d3.select("body")
    .append("svg")
    .attr("width", width)
    .attr("height", height);

  simulation = d3.forceSimulation()
    .force("link", d3.forceLink().id(d => d.id).distance(300))
    .force("charge", d3.forceManyBody().strength(-800))
    .force("center", d3.forceCenter(width / 2, height / 2))
    .force("x", d3.forceX(width / 2).strength(0.1))
    .force("y", d3.forceY(height / 2).strength(0.1));

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

  // 논문 제목 추가
  nodeGroup.append("text")
    .text(d => d.id) // 논문 제목 표시
    .attr("fill", "gray")
    // .attr("font-size", d => Math.max(8, d.size / 5)) // 크기를 원 크기에 비례하게 설정
    // .attr("text-anchor", "middle")
    .attr("dx", d => d.size / 2)
    .attr("dy", d => d.size / 10) // 제목을 인용 수 아래에 배치
    .attr("class", "title-label")
  // .call(wrapText, 100); // 긴 제목을 자동 줄바꿈 (아래에 wrapText 함수 추가됨)

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
  console.log("Graph created successfully!"); // ✅ 디버깅용 로그 추가
}

function dragstarted(event) {
  if (!event.active) {
    simulation.alphaTarget(0.3).restart()
  }
  event.subject.fx = event.subject.x;
  event.subject.fy = event.subject.y

  // ⬇⬇⬇ 드래그 발생 시 연도 라벨 제거 ⬇⬇⬇
  svg.select(".year-labels").remove();

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

function sortByYearAndCitation() {
  // 1️⃣ 연도별로 그룹화
  const yearGroups = {};
  nodes.forEach(node => {
    if (!yearGroups[node.year]) {
      yearGroups[node.year] = [];
    }
    yearGroups[node.year].push(node);
  });

  // 2️⃣ 각 연도 그룹을 인용 수 기준으로 정렬
  Object.keys(yearGroups).forEach(year => {
    yearGroups[year].sort((a, b) => b.citationCount - a.citationCount);
  });

  // 3️⃣ 화면 너비를 연도 개수로 나누어 x 위치 결정
  const uniqueYears = Object.keys(yearGroups).sort((a, b) => a - b); // 연도 오름차순 정렬
  const yearSpacing = width / (uniqueYears.length + 1); // 연도별 x 간격
  const verticalSpacing = 80; // 같은 연도 내 세로 간격

  uniqueYears.forEach((year, yearIndex) => {
    const yearNodes = yearGroups[year];
    const centerX = yearSpacing * (yearIndex + 1); // 해당 연도의 X 위치

    yearNodes.forEach((node, nodeIndex) => {
      node.fx = centerX;
      node.fy = height / 2 + nodeIndex * verticalSpacing - (yearNodes.length * verticalSpacing) / 2;
    });
  });

  // 4️⃣ Force Simulation 다시 실행
  simulation.alpha(1).restart();

  // 5️⃣ 연도를 화면 하단에 추가 (버튼을 눌렀을 때만 보이게)
  svg.select(".year-labels").remove(); // 기존 연도 라벨 삭제

  svg.append("g")
    .attr("class", "year-labels")
    .selectAll("text")
    .data(uniqueYears)
    .enter()
    .append("text")
    .text(d => d) // 연도 표시
    .attr("x", (d, i) => yearSpacing * (i + 1))
    .attr("y", height - 20)
    .attr("text-anchor", "middle")
    .attr("font-size", "16px")
    .attr("fill", "black")
    .style("opacity", 0) // 처음에는 숨김
    .transition().duration(500) // 애니메이션 효과
    .style("opacity", 1);
}
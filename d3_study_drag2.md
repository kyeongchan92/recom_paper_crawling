# Drag 2
아래 코드를 이해해보자.

```js
<!DOCTYPE html>
<html lang="en">

<head>
  <meta charset="UTF-8">
  <title>drag</title>
  <script src="https://d3js.org/d3.v7.min.js"></script>
</head>

<body>

  <div id="d3Graph" style="border: lightgray solid 1px;display: inline-block;width: 100%;"></div>

  <script>
    var divWidth = document.querySelector("#d3Graph").clientWidth;
    var vhWindowRatio = 420 / 590;

    document.querySelector("#d3Graph").style.height = parseInt(divWidth * vhWindowRatio) + "px";
    var divHeight = document.querySelector("#d3Graph").clientHeight;
    
    d3.select("#d3Graph").append("canvas");

    var canvas = document.querySelector("canvas");
    var context = canvas.getContext("2d");
    canvas.width = divWidth;
    canvas.height = divHeight;

    var width = canvas.width;
    var height = canvas.height;
    var rRatio = width / 590;
    var radius = 20 * rRatio;
    var circles = d3.range(165).map(function (a) {
      return { x: (a % 15) * (radius + 1) * 2, y: Math.floor(a / 15) * (radius + 1) * 2 }
    });

    var simulation = d3.forceSimulation(circles)
      .force("collide", d3.forceCollide(radius + 1)
                          .iterations(4))
      .on("tick", drawCircles);

    d3.select(canvas)
      .call(d3.drag()
      .container(canvas)
      .subject(dragsubject)
      .on("start", dragstarted)
      .on("drag", dragged)
      .on("end", dragended));

    function drawCircles() {
      context.clearRect(0, 0, width, height);
      context.save();
      context.beginPath();
      circles.forEach(drawCircle);

      context.fill();
      context.strokeStyle = "Gold";
      context.stroke()
    }

    function drawCircle(a) {
      context.moveTo(a.x + radius, a.y);
      context.arc(a.x, a.y, radius, 0, 2 * Math.PI)
    }

    function dragsubject(event) {
      return simulation.find(event.x, event.y, radius)
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
    
    (window.onload = function () {
      width = document.querySelector("#d3Graph").clientWidth;
      document.querySelector("#d3Graph").style.height = parseInt(width * vhWindowRatio) + "px";
      height = document.querySelector("#d3Graph").clientHeight;

      canvas.width = width;
      canvas.height = height
    });
  </script>

</body>

</html>
```

## forceSimulation

먼저 ```circles```라는 변수부터 보자.
```js
var circles = d3.range(165).map(function (a) {
    return { x: (a % 15) * (radius + 1) * 2, y: Math.floor(a / 15) * (radius + 1) * 2 }
});
```

- ```var circles = d3.range(165).map(function (a) {...``` : 165개의 원(circle) 좌표를 생성
  - ```d3.range(n)```은 0부터 n-1까지의 숫자가 들어 있는 배열을 생성. 즉, ```d3.range(165)```는 ```[0, 1, 2, ..., 164]```의 배열을 반환.
- ```.map(function (a) {...})``` : 각 원의 위치 (x, y)를 계산하는 함수
  - ```a```는 0~164까지의 숫자이고, 이를 이용해서 원의 (x, y) 좌표를 결정
  - 원 사이에 **적절한 간격(radius + 1)**을 둬서 겹치지 않도록 함

![alt text](image-3.png)
circles 변수를 찍어보면 165개의 요소가 있는 배열이며, 각 요소는 x, y 값을 갖는다.



그 다음 D3의 ```forceSimulation```에 대해 알아보자. D3의 물리 기반(force layout) 시뮬레이션을 사용해서 원(circle)들이 서로 겹치지 않도록 함. 각 원이 충돌하지 않도록 force simulation을 적용해서 자연스럽게 퍼지게 만드는 방식.

```js
var simulation = d3.forceSimulation(circles).force(
                                            "collide", 
                                            d3.forceCollide(radius + 1).iterations(4)
                                            )
                                            .on("tick", drawCircles);
```

✅ **```d3.forceSimulation(circles)```**
- D3의 force simulation(물리 엔진)을 생성하고, circles 배열을 시뮬레이션에 추가.
- circles는 원들의 초기 위치를 담은 배열이고, 시뮬레이션이 실행되면서 원들의 위치가 업데이트됨.

✅ **```.force("collide", d3.forceCollide(radius + 1).iterations(4))```**
- 원들끼리 서로 겹치지 않도록 하는 충돌(Collision) force를 추가.
- d3.forceCollide(radius + 1):
    - 각 원(circle)의 반지름 + 1(px) 만큼의 거리를 유지하면서, 서로 겹치지 않도록 함.
    - 원의 중심 간 거리가 radius + 1 이하가 되면 서로 밀어내는 효과 발생.
- ```.iterations(4)```:
  - 충돌을 더 정확하게 처리하기 위해 4번 반복하여 보정.
  - 값을 증가시키면 원들이 더 부드럽게 퍼지지만, 성능이 조금 더 느려질 수 있음.



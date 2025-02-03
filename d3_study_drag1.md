# 드래그
### 드래그를 위한 d3.call
아래 코드를 이해해보자.
```js
var div = d3.selectAll("div")
    .call(
        d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended)
    );
const divMsg = div.append("p");

var dragged
var draggedCount = 0;

// 드래그 시작 호출되는 함수
function dragstarted() {
    divMsg.text("");
    divMsg.append("p").text("dragstarted: " + new Date());
    dragged = divMsg.append("p");
    draggedCount = 0;
}

// 드래그하는 동안 호출되는 함수
function dragged() {
    dragged.text("dragged: " + (draggedCount++));
}

// 드래그 종료시 호출되는 함수
function dragended() {
    divMsg.append("p").text("dragended  " + new Date());
    dragging = false;

    // d3.selectAll("div")
    //     .on(".drag", null);
}
```

일단 아래 부분을 보자.

```js
var div = d3.selectAll("div")
    .call(
        d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended)
    );
```

```call()```은 현재 **선택된 요소에 함수를 적용할 때** 사용합니다.

❓**왜 ```call(d3.drag())```을 써야 할까?**

D3에서 요소를 드래그 가능하게 만들려면 ```d3.drag()```를 적용해야 합니다. 하지만 ```d3.drag()``` 자체는 드래그 이벤트를 정의하는 함수일 뿐, 요소에 바로 적용되지는 않습니다.

그래서 ```.call(d3.drag())```을 사용하여 circle 요소가 드래그 이벤트를 감지하도록 만듭니다.

공식문서에 보면 다음과 같이 써있다.

![alt text](image.png)
즉, drag behavior를 특정 selection된 것에 적용할 때, 이 함수 drag는 바로 실행되지는 않기 때문에 selection.call을 통해 드래그가 실행될 수 있다는 것.

**📌 ```on()``` 메서드는 언제, 왜 쓰는 걸까?**

D3.js에서 ```.on()```은 이벤트 리스너를 추가할 때 사용됩니다.
즉, 특정 이벤트(클릭, 마우스오버, 드래그 등)가 발생했을 때 실행할 동작을 정의할 수 있습니다. on의 기본 문법 : 

```js
d3.select("circle")
  .on("event", function(event, d) {
    // 이벤트 발생 시 실행할 코드
  });
```
- ```"event"```: 이벤트 이름 (예: "click", "mouseover", "drag", etc.)
- ```event```: 이벤트 객체 (마우스 좌표, 키 입력 등)
- ```d```: 해당 요소의 데이터

예제 : 마우스를 올리면 색상 변경
```js
d3.select("circle")
  .on("mouseover", function () {
    d3.select(this).attr("fill", "red");
  })
  .on("mouseout", function () {
    d3.select(this).attr("fill", "blue");
  });
```
- mouseover: 마우스를 올리면 색이 빨간색으로 변함.
- mouseout: 마우스를 치우면 색이 파란색으로 돌아감.

난 초보니까 listener라는 개념을 보자.

> **listener 개념**
> 
> 👉 이벤트 리스너(listener)는 특정 이벤트(클릭, 드래그, 키 입력 등)가 발생했을 때 실행되는 함수(콜백 함수)를 의미해.
> 즉, listener는 "어떤 이벤트가 발생하면 실행할 코드"를 담고 있는 함수.
>
> listener가 어떻게 동작하는지 예제
> ```js
> document.getElementById("myButton").> addEventListener("click", function() {
>   alert("버튼이 클릭됨!");
> });
> ```
> - ```"click"```: 이벤트 유형 (버튼이 클릭될 때)
>   - ```"click"```등은 이미 정의되어 있으며, '이벤트 타입'이라고 부른다.
>   - ```"mousedown"``` : "마우스 버튼을 누를 때" 등이 있다.
> - ```function() {...}```: 이 이벤트가 발생하면 실행될 리스너 함수
> - ```"click"``` 같은 이벤트가 발생하면 브라우저가 감지하고, 지정된 함수를 실행

---

### dragstarted() 함수

```js
const divMsg = div.append("p");
var dragged
var draggedCount = 0;

// 드래그 시작 호출되는 함수
function dragstarted() {
    divMsg.text("");
    divMsg.append("p").text("dragstarted: " + new Date());
    dragged = divMsg.append("p");
    draggedCount = 0;
}

// 드래그하는 동안 호출되는 함수
function dragged() {
    dragged.text("dragged: " + (draggedCount++));
}
```

- ```div.append("p")``` → 요소를 추가해서 divMsg에 저장.
- ```divMsg.text("")``` → 기존 내용을 지움. 드래그가 시작할 때마다 divMsg가 가리키는 요소 안의 기존 텍스트를 삭제.
- ```divMsg.append("p").text("dragstarted: " + new Date())``` → 드래그가 시작될 때 시간 정보 표시. 새로운 요소를 추가해서 "dragstarted: 현재 시간"을 표시
![alt text](image-2.png)
- ```dragged = divMsg.append("p")```→ 새로운 요소를 하나 추가하고, 이걸 dragged 변수에 저장. 이 요소는 드래그 중(dragged() 함수에서) 변경될 예정
- ```dragged.text("dragged: " + (draggedCount++));```→ 드래그할 때 숫자가 증가하면서 업데이트됨.
---
title: "React"
date: 2026-04-08T10:42:56+08:00
tags:
  - React
  - 前端
draft: false
---

文档：[https://17.reactjs.org/docs/getting-started.html]

## 核心要点

| 你想做的事       | React 里常用               | Vue 里常用     |
| ----------- | ----------------------- | ----------- |
| 页面加载后执行一次   | useEffect(..., [])      | onMounted   |
| 页面销毁前清理     | useEffect 返回清理函数        | onUnmounted |
| 监听某个值变化     | useEffect(..., [value]) | watch       |
| 自动追踪依赖执行副作用 | useEffect（手动写依赖）        | watchEffect |
| 根据状态计算新值    | useMemo                 | computed    |


## 代码整理：
hello world
注意需要使用==type="text/jsx"==
```js
<!DOCTYPE html>  
<html lang="en">  
<head>  
    <meta charset="UTF-8">  
    <title>Title</title>  
    <script src="https://unpkg.com/react@18/umd/react.development.js"></script>  
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>  
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>  
</head>  
<body>  
<div id="root"></div>  
</body>  
<script type="text/jsx">  
    const element = <h1>Hello, world</h1>;  
    ReactDOM.render(element, document.getElementById('root'));  
</script>  
</html>
```

时钟：
```js
<!DOCTYPE html>  
<html lang="en">  
<head>  
    <meta charset="UTF-8">  
    <title>Title</title>  
    <script src="https://unpkg.com/react@17/umd/react.development.js"></script>  
    <script src="https://unpkg.com/react-dom@17/umd/react-dom.development.js"></script>  
    <style>  
    </style></head>  
<body>  
<div id="root"></div>  
</body>  
<script type="text/jsx">  
    function tick() {  
        const element = (  
            <div>  
                <h1>Hello, world!</h1>  
                <h2>It is {new Date().toLocaleTimeString()}.</h2>  
            </div>        );  
        ReactDOM.render(element, document.getElementById('root'));  
    }  
  
    setInterval(tick, 1000);  
</script>  
</html>
```
jsx:
```js
<script type="text/jsx">  
    const name = 'lkr';  
    const element = <h1>Hello,{name}</h1>  
    ReactDOM.render(  
        element,  
        document.getElementById('root')  
    );  
</script>
```
使用函数调用
```js
<script type="text/jsx">  
    function formatName(user){  
        return user.firstName+' '+user.lastName;  
    }  
  
    const user = {  
        firstName:'liao',  
        lastName:'kongrui'  
    }  
  
    const element = (  
        <div>  
            <h1>Hello,{formatName(user)}</h1>  
        </div>    )  
  
    ReactDOM.render(  
        element,  
        document.getElementById('root')  
    )  
</script>
```
```js
<script type="text/jsx">  
    const user = {  
        firstName: 'liao',  
        lastName: 'kongrui'  
    }  
  
    function formatName(user) {  
        return user.firstName + ' ' + user.lastName;  
    }  
  
    function getGreeting(user) {  
        if (user) {  
            return (<h1>hello,{formatName(user)}</h1>);  
        } else {  
            return (<h1>hello,stronger</h1>)  
        }  
    }  
  
    const element = (  
        <div>  
            <h1>{getGreeting(user)}</h1>  
            <h1>{getGreeting()}</h1>  
        </div>    )  
  
    ReactDOM.render(  
        element,  
        document.getElementById('root')  
    )  
</script>
```
组件思想
```js
<script type="text/jsx">  
    function Welcome(prop) {  
        return <h1>Welcome,{prop.name}</h1>  
    }  
  
    const element = <Welcome name="rui"/>  
  
    ReactDOM.render(  
        element,  
        document.getElementById('root')  
    )  
</script>
```
App封装思想
```js
<script type="text/jsx">  
    function Welcome(prop) {  
        return <h1>Welcome,{prop.name}</h1>  
    }  
  
    function App() {  
        return (  
            <div>  
                <Welcome name="rui"/>  
                <Welcome name="xiaoliao"/>  
                <Welcome name="zhangsan"/>  
            </div>        )  
    }  
  
    ReactDOM.render(  
        <App/>,  
        document.getElementById('root')  
    )  
</script>
```
组件信息传递

```js
<!DOCTYPE html>  
<html lang="en">  
<head>  
    <meta charset="UTF-8">  
    <title>Title</title>  
    <script src="https://unpkg.com/react@17/umd/react.development.js"></script>  
    <script src="https://unpkg.com/react-dom@17/umd/react-dom.development.js"></script>  
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>  
    <style>  
    </style></head>  
<body>  
<div id="root"></div>  
</body>  
<script type="text/jsx">  
    function Comment(props) {  
        return (  
            <div className="Comment">  
                <div className="UserInfo">  
                    <Author author={props.author}/>  
                </div>                <div>                    text: {props.text}  
                </div>  
                <div>                    date: {formatDate(props.date)}  
                </div>  
            </div>        )  
    }  
  
    function Author(props) {  
        return (  
            <div className="UserInfo">  
                <Avatar author={props.author}/>  
                <div className="UserInfo-name">  
                    {props.author.name}  
                </div>  
            </div>        );  
    }  
  
    function Avatar(props) {  
        return (  
            <img className="Avatar"  
                 src={props.author.avatarUrl}  
                 alt={props.author.name}  
            />  
        );  
    }  
      
    const comment = {  
        author: {  
            name: 'rui',  
            avatarUrl: 'https://www.baidu.com/img/PCtm_d9c8750bed0b3c7d089fa7d55720d6cf.png'  
        },  
        text: '百度一下吧',  
        date: new Date(),  
    }  
  
    function formatDate(date) {  
        return date.toLocaleDateString()  
    }  
  
    function App() {  
        return (  
            <div>  
                <Comment author={comment.author} text={comment.text} date={comment.date}/>  
            </div>        )  
    }  
  
    ReactDOM.render(  
        <App/>,  
        document.getElementById('root')  
    )  
</script>  
</html>
```
定时器改造
```js
<script type="text/jsx">  
    class Clock extends React.Component {  
        // data  
        constructor(props) {  
            super(props);  
            // 初始化state，包含一个date属性，值为当前日期时间  
            this.state = {date: new Date()}  
        }  
  
        // mounted  
        componentDidMount() {  
            // 设置定时器，每1000毫秒（即1秒）执行一次tick方法  
            this.timeID = setInterval(() => this.tick(), 1000)  
        }  
  
        // 组件卸载前执行的方法，用于清除定时器  
        // beforeDestroy  
        componentWillUnmount() {  
            clearInterval(this.timeID)  
        }  
  
        //methods  
        tick() {  
            // 调用setState方法，更新date属性为当前日期时间  
            this.setState({  
                date: new Date()  
            })  
        }  
  
        render() {  
            return (  
                <div>  
                    <h1>Hello, world!</h1>  
                    <h2>It is {this.state.date.toLocaleTimeString()}.</h2>  
                </div>            )  
        }  
    }  
  
  
    ReactDOM.render(  
        <Clock/>,  
        document.getElementById('root')  
    );  
    </script>
```

todoList
```jsx
<!DOCTYPE html>

<html lang="en">

<head>

<meta charset="UTF-8">

<title>Title</title>

<script src="https://unpkg.com/react@18/umd/react.development.js"></script>

<script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>

<script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>

</head>

<body>

  

<div id="root"></div>

  

</body>

<script type="text/jsx">

function TodoList() {

const [todos, setTodos] = React.useState([]);

const [inputValue, setInputValue] = React.useState('');

  

// 添加任务

const handleAdd = () => {

if (inputValue.trim() === '') return;

setTodos([...todos, {

id: Date.now(),

text: inputValue,

completed: false

}]);

setInputValue('');

};

  

// 删除任务

const handleDelete = (id) => {

setTodos(todos.filter(todo => todo.id !== id));

};

  

// 切换任务状态

const handleToggle = (id) => {

setTodos(todos.map(todo =>

todo.id === id ? {...todo, completed: !todo.completed} : todo

));

};

  

return (

<div style={{maxWidth: '500px', margin: '20px auto', padding: '20px'}}>

<h1>待办事项</h1>

{/* 输入区域 */}

<div style={{marginBottom: '20px'}}>

<input

type="text"

value={inputValue}

onChange={(e) => setInputValue(e.target.value)}

onKeyPress={(e) => e.key === 'Enter' && handleAdd()}

placeholder="请输入待办事项"

style={{padding: '5px', marginRight: '10px'}}

/>

<button onClick={handleAdd}>添加</button>

</div>

  

{/* 列表区域 */}

<ul style={{listStyle: 'none', padding: 0}}>

{todos.map(todo => (

<li key={todo.id} style={{

display: 'flex',

alignItems: 'center',

marginBottom: '10px',

padding: '10px',

backgroundColor: '#f5f5f5',

borderRadius: '5px'

}}>

<input

type="checkbox"

checked={todo.completed}

onChange={() => handleToggle(todo.id)}

/>

<span style={{

marginLeft: '10px',

flex: 1,

textDecoration: todo.completed ? 'line-through' : 'none'

}}>

{todo.text}

</span>

<button onClick={() => handleDelete(todo.id)}>删除</button>

</li>

))}

</ul>

</div>

);

}

  

const root = ReactDOM.createRoot(document.getElementById('root'));

root.render(<TodoList />);

</script>

</html>
```


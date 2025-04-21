import {useState} from 'react';
import './App.css';
import Square from './Pages/Square.jsx';


function Board({xIsNext, squares, onPlay}) {
  const indices = [0, 1, 2, 3, 4, 5, 6, 7, 8]
  //const [xIsNext, setXIsNext] = useState(true);
  //const [squares, setSquares] = useState(Array(9).fill(null));

  const winner = calculateWinner(squares);
  let status;
  if (winner) {
    status = "Winner: " + winner;
  }
  else {
    status = "Next player: " + (xIsNext ? "X" : "O");
  }

  function handleClick(i) {
      if (squares[i] || calculateWinner(squares)) return; //if already filled
      const nextSquares = squares.slice(); //very quick and standard way. React relies on the reliability (immutability) of its objects
      xIsNext ? nextSquares[i] = 'X' : nextSquares[i] = 'O';
      //setXIsNext(!xIsNext);
      //setSquares(nextSquares);
      onPlay(nextSquares);
  }

  return (
    <div className="App">
      <header className="App-header">
      <div className="board">
        {indices.map((index) => (
          <Square key={index} value={squares[index]} onSquareClick={() => handleClick(index)}/>
        ))}
      </div>
      <p>
        {status}
      </p>

    </header>
    </div>
  );
}

export default function Game() {
  //const [xIsNext, setXIsNext] = useState(true);
  const [history, setHistory] = useState([Array(9).fill(null)]);
  const [currentMove, setCurrentMove] = useState(0);
  const xIsNext = currentMove % 2 === 0; //this is the current player
  const currentSquares = history[currentMove];

  function handlePlay(nextSquares) {
    const nextHistory = [...history.slice(0, currentMove + 1), nextSquares];
    setHistory(nextHistory); //...history is the spread operator, which is a way to copy an array
    setCurrentMove(nextHistory.length - 1);
    //setXIsNext(!xIsNext);
    console.log(history);
  }

  function jumpTo(nextMove) {
    setCurrentMove(nextMove);
    //setXIsNext(nextMove % 2 == 0);
  }

  const moves = history.map((squares, move) => { //map's second argument is the index
    let description;
    if (move > 0) {
      description = 'Go to move #' + move;
    }
    else {
      description = 'Go to game start';
    }
    return (
      <li key={move}>
        <button onClick={() => jumpTo(move)}>{description}</button>
      </li>
    );
  })

  return (
    <div className="game">
      <div className="game-board">
        <Board xIsNext={xIsNext} squares={currentSquares} onPlay={handlePlay}/>
      </div>
      <div className="game-info">
        <div>{/* status */}</div>
        <ol>{moves}</ol>
      </div>
    </div>      
  );
}

//export default App;

function calculateWinner(squares) {
  const lines = [
    [0, 1, 2],
    [3, 4, 5],
    [6, 7, 8],
    [0, 3, 6],
    [1, 4, 7],
    [2, 5, 8],
    [0, 4, 8],
    [2, 4, 6]
  ];
  
  for (let i = 0; i < lines.length; i++) {
    const [a, b, c] = lines[i];
    if (squares[a] && squares[a] === squares[b] && squares[a] === squares[c]) {
      return squares[a];
    }
  }
  
  return null;
}

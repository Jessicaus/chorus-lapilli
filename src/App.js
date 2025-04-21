import {useState} from 'react';
import './App.css';

import Board from './Pages/Board.jsx';

export default function Game() {
  //const [xIsNext, setXIsNext] = useState(true);
  const [history, setHistory] = useState([Array(9).fill(null)]);
  const [currentMove, setCurrentMove] = useState(0);
  const xIsNext = currentMove % 2 === 0; //this is the current player
  const isPlacementPhase = currentMove < 6; //is it placement or moving phase?
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
        <Board xIsNext={xIsNext} isPlacementPhase={isPlacementPhase} squares={currentSquares} onPlay={handlePlay}/>
      </div>
      <div className="game-info">
        <div>{/* status */}</div>
        <ol>{moves}</ol>
      </div>
    </div>      
  );
}

//export default App;

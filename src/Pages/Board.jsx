import '../styles/Board.css';
import Square from '../Pages/Square.jsx';

export default function Board({xIsNext, isPlacementPhase, squares, onPlay}) {
  const indices = [0, 1, 2, 3, 4, 5, 6, 7, 8]
  let selected = null;
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
      if (calculateWinner(squares)) return; //if already filled
      const nextSquares = squares.slice(); //very quick and standard way. React relies on the reliability (immutability) of its objects
      if (!isPlacementPhase) {
        const player = xIsNext ? "X" : "O";
        if (squares[i] === player) {
            selected = i;
            console.log("selected=" + selected);
        }
        else if (selected !== null) {
            if (squares[i] === null && isAdjacent(i, selected)) {
                nextSquares[i] = squares[selected];
                nextSquares[selected] = null;
                if (player === squares[4]) { //if the middle square is occupied by the next player
                    if(calculateWinner(nextSquares)) { //if the next move is the winning move
                        onPlay(nextSquares);
                    }
                    else if (selected === 4) { //if next move is not winning move and is the middle square
                        onPlay(nextSquares);
                    } //else, nothing happens
                }
                else {
                    onPlay(nextSquares);
                }
            }
            selected = null;
        }
      }
      else if (!squares[i]) {
        xIsNext ? nextSquares[i] = 'X' : nextSquares[i] = 'O';
        onPlay(nextSquares);
      }
      //setXIsNext(!xIsNext);
      //setSquares(nextSquares);
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

function isAdjacent(x, y) {
    const rx = Math.floor(x / 3), cx = x % 3;
    const ry = Math.floor(y / 3), cy = y % 3;
    return (Math.abs(rx - ry) <= 1 && Math.abs(cx - cy) <= 1);
}

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
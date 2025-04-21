export default function Square({value, onSquareClick}) {
    //const [value, setValue] = useState(null);

    return (
    <button className="square" onClick={onSquareClick}>
        {value}
    </button>
    );
}
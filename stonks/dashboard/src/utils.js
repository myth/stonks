function colorize(value, suffix) {
    let color = "text-green"
  
    if (value < 0) color = "text-red"
  
    if (suffix) return <span className={color}>{value}</span>
    else return <span className={color}>{value} {suffix}</span>
  }

export {
    colorize,
}

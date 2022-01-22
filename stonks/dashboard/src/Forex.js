function Forex(props) {
  const keys = Object.keys(props.forex)
  const pos = keys.map(k => {
    const p = props.forex[k]

    return (
      <tr key={p.name}>
        <td className="text-left">{p.name}</td>
        <td>{p.market_price} <small>NOK</small></td>
      </tr>
    )
  })

  return (
    <table id="forex">
      <thead>
        <tr>
          <th className="text-left">Name</th>
          <th>Market Price</th>
        </tr>
      </thead>
      <tbody>{pos}</tbody>
    </table>
  )
}

export default Forex

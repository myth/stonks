function Composition(props) {
  const keys = Object.keys(props.composition)
  const pos = keys.map(k => {
    const c = props.composition[k]

    return (
      <tr key={k}>
        <td className="text-left">{k}</td>
        <td>{c} <small>%</small></td>
      </tr>
    )
  })

  return (
    <table id="composition">
      <thead>
        <tr>
          <th className="text-left">Asset</th>
          <th>Allocation</th>
        </tr>
      </thead>
      <tbody>{pos}</tbody>
    </table>
  )
}

export default Composition

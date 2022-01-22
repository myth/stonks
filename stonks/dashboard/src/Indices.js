import { colorize } from './utils'

function Indices(props) {
  const keys = Object.keys(props.indices)
  const idx = keys.map(k => {
    const p = props.indices[k]

    return (
      <tr key={p.name}>
        <td className="text-left">{p.name}</td>
        <td>{p.last.toFixed(2)}</td>
        <td>{colorize(p.change)} <small>%</small></td>
        <td>{colorize(p.change_7d)} <small>%</small></td>
      </tr>
    )
  })

  return (
    <table id="indices">
      <thead>
        <tr>
          <th className="text-left">Name</th>
          <th>Last</th>
          <th>Change 1D</th>
          <th>Change 7D</th>
        </tr>
      </thead>
      <tbody>{idx}</tbody>
    </table>
  )
}

export default Indices

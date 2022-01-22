import { colorize } from './utils'

import './css/Positions.css'

function Positions(data) {
  const pos = data.positions.sort((a, b) => a.name > b.name).map(p => {
    return (
      <tr key={p.name}>
        <td className="text-left">{p.name}</td>
        <td className="hide-medium">{p.volume}</td>
        <td className="hide-medium">{p.market_price} <small>{p.currency}</small></td>
        <td>{p.market_value} <small>NOK</small></td>
        <td>{colorize(p.net_return_percent)} <small>%</small></td>
        <td className="hide-extra-small">{colorize(p.net_return)} <small>NOK</small></td>
        <td className="hide-medium">{p.asset}</td>
        <td className="hide-small">{p.allocation} <small>%</small></td>
      </tr>
    )
  })

  return (
    <section>
      <div className="banner">Positions</div>
      <div className="banner-table" id="positions">
        <table>
          <thead>
            <tr>
              <th className="text-left">Name</th>
              <th className="hide-medium">Position</th>
              <th className="hide-medium">Market Price</th>
              <th>Market Value</th>
              <th>Net Return</th>
              <th className="hide-extra-small">Unrealized</th>
              <th className="hide-medium">Asset</th>
              <th className="hide-small">Allocation</th>
            </tr>
          </thead>
          <tbody>{pos}</tbody>
        </table>
      </div>
    </section>
  )
}

export default Positions

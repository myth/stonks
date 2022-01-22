import React from 'react'

class TickerFeed extends React.Component {
  constructor(props) {
    super(props)
    this.limit = props.limit !== undefined ? props.limit : 12
    this.state = { latest: [] }
  }

  addTicker(t) {
    this.setState({
      latest: [[new Date().toTimeString().substr(0, 8), t], ...this.state.latest].slice(0, this.limit)
    })
  }

  render() {
    let i = 0
    const items = this.state.latest.map(t => (
      <tr key={i++}>
        <td className="text-left">{t[0]}</td>
        <td className="text-left">{t[1].name}</td>
        <td>{t[1].market_price} <small>{t[1].currency ? t[1].currency : "NOK"}</small></td>
      </tr>
    ))

    return (
      <table>
        <thead>
          <tr>
            <th className="text-left">Time</th>
            <th className="text-left">Name</th>
            <th>Market Price</th>
          </tr>
        </thead>
        <tbody>{items}</tbody>
      </table>
    )
  }
}

export default TickerFeed

import React from 'react'

const formatCounterUnit = c => {
  if (c >= 1000) return `${(c / 1000).toFixed(1)}K`
  else return c
}

class Status extends React.Component {
  constructor(props) {
    super(props)
    this.state = {}
  }

  render() {
    const keys = Object.keys(this.state)
    const status = keys.map(k => {
      const s = this.state[k]

      return (
        <tr key={k}>
          <td className="text-left">{k}</td>
          <td>{formatCounterUnit(s.messages)}</td>
          <td>{formatCounterUnit(s.errors)}</td>
          <td>{formatCounterUnit(s.restarts)}</td>
        </tr>
      )
    })

    return (
      <table id="status">
        <thead>
          <tr>
            <th className="text-left">Collector</th>
            <th>Messages</th>
            <th>Errors</th>
            <th>Restarts</th>
          </tr>
        </thead>
        <tbody>{status}</tbody>
      </table>
    )
  }
}

export default Status

import React from 'react'

import './css/Header.css'

const COLORS = {
  "connected": "text-green",
  "reconnecting": "text-orange",
  "disconnected": "text-red",
}

class Header extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
          status: "disconnected",
          lastUpdate: new Date()
        }
    }

    render() {
      return (
        <header id="header">
          <div id="connection">
            Stonks is <span className={COLORS[this.state.status]}><strong>{this.state.status}</strong></span>
          </div>
          <div id="updated">Updated <b>{this.state.lastUpdate.toTimeString().substr(0, 8)}</b></div>
        </header>
      )
    }
}

export default Header

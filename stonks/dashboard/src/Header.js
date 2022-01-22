import React from 'react'

import './css/Header.css'

class Header extends React.Component {
    constructor(props) {
        super(props)
        this.state = { connected: false, lastUpdate: new Date() }
    }

    render() {
      return (
        <header id="header">
          <div id="connection">
            Stonks is <span className={this.state.connected ? "text-green" : "text-red"}>
              <strong>{this.state.connected ? "connected" : "not connected"}</strong>
            </span>
          </div>
          <div id="updated">Updated <b>{this.state.lastUpdate.toTimeString().substr(0, 8)}</b></div>
        </header>
      )
    }
}

export default Header

import { colorize } from './utils'
import React from 'react'

import './css/Summary.css'

function SummaryPlate(props) {
  let val = <span>{ props.colorize ? colorize(props.value) : props.value }</span>

  if (props.suffix) val = <span>{val} <small className="summary-plate-value-suffix">{props.suffix}</small></span>

  return (
    <div className="summary-plate">
      <div className="summary-plate-value">{val}</div>
      <div className="summary-plate-title">{props.title}</div>
    </div>
  )
}

class Summary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { marketValue: 0, netReturn: 0.0, netReturnPercent: 0.0 }
  }

  render() {
    const netReturnAfterTax = Math.round(this.state.netReturn - this.state.netReturn * 0.3168)

    return (
      <div id="summary">
        <SummaryPlate title="Market Value" value={this.state.marketValue} suffix="NOK"/>
        <SummaryPlate title="Net Return" value={this.state.netReturnPercent} suffix="%" colorize />
        <SummaryPlate title="Unrealized" value={this.state.netReturn} suffix="NOK" colorize />
        <SummaryPlate title="Unrealized After Tax" value={netReturnAfterTax} suffix="NOK" colorize />
      </div>
    )
  }
}

export {
  Summary,
  SummaryPlate,
}

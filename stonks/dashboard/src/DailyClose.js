import Chart from "react-apexcharts"
import React from "react"


export default class DailyClose extends React.Component {
  constructor(props) {
    super(props)
    this.state = {
      options: {
        chart: {
          id: "chart",
          type: "candlestick",
          animations: { enabled: false },
          background: "black"
        },
        plotOptions: {
          candlestick: {
            colors: {
              upward: '#086814',
              downward: '#880707'
            }
          }
        },
        grid: { show: false },
        xaxis: { axisTicks: { show: false }, axisBorder: { show: false }, type: "datetime" },
        yaxis: { axisTicks: { show: false }, labels: { show: false }, axisBorder: { show: false }, },
        // stroke: { curve: "straight", width: 3 },
        theme: { mode: "dark" },
        // colors: ["#7e9724"]
      },
      series: [{ name: "Daily", data: [] }]
    }
  }

  setCloses(data) {
    const items = data.map(d => {
      return {
        x: new Date(d["date"]).getTime(),
        y: [d["open"], d["high"], d["low"], d["close"]]
      }
    })
    this.setState({ series: [{ name: "Daily", data: items}]})
  }

  render() {
    const items = this.state.series.map(c => <div key={c["date"]}>{c["open"]} | {c["high"]} | {c["low"]} | {c["close"]}</div>)
    return (
      <section id="daily-closes">
        <Chart options={this.state.options} series={this.state.series} type="candlestick" width="100%" height="320" />
      </section>
    )
  }
}

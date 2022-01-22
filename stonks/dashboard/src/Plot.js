import Chart from "react-apexcharts"
import React from "react"

const MAX_TICKS = 400
const SERIES_NAME = "Market Value"

class Plot extends React.Component {
  constructor(props) {
    super(props)

    this.state = {
      options: {
        chart: {
          id: "chart",
          animations: { enabled: false },
          background: "black"
        },
        grid: { show: false },
        xaxis: { categories: [], axisTicks: { show: false }, labels: { show: false }, axisBorder: { show: false }, },
        yaxis: { show: false, axisTicks: { show: false }, labels: { show: false }, axisBorder: { show: false }, },
        stroke: { curve: "straight", width: 3 },
        theme: { mode: "dark" },
        colors: ["#7e9724"]
      },
      series: [{ name: SERIES_NAME, data: [] }]
    }
  }

  addPoint(val) {
    const data = this.state.series[0].data.slice(0)
    data.push(val)
    if (data.length > MAX_TICKS) data.shift()

    this.setState({
      series: [{ name: SERIES_NAME, data }]
    })
  }

  setData(data) {
    this.setState({
      series: [{ name: SERIES_NAME, data }]
    })
  }

  render() {
    return (
      <>
        <Chart options={this.state.options} series={this.state.series} type="line" width="100%" height="320" />
      </>
    )
  }
}

export default Plot

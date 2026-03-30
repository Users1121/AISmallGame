import React from 'react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts'
import './NationStatsChart.css'

// 支持 gameStore 的英文格式和中文格式
interface DataPointInput {
  month: string
  food?: number
  population?: number
  economy?: number
  energy?: number
  食物?: number
  人口?: number
  经济?: number
  能源?: number
}

interface NationStatsChartProps {
  data: DataPointInput[]
  nationName: string
}

const NationStatsChart: React.FC<NationStatsChartProps> = ({ data, nationName }) => {
  const calculatePercentageChange = (current: number, initial: number) => {
    if (initial === 0) return 0
    return ((current - initial) / Math.abs(initial) * 100).toFixed(2)
  }

  // 统一取出数值，兼容英文(food/population/parts/energy)和中文(食物/人口/零件/能源)两种格式
  const getValue = (point: DataPointInput, key: 'food' | 'population' | 'economy' | 'energy') => {
    const enMap = { food: 'food', population: 'population', economy: 'economy', energy: 'energy' }
    const zhMap = { food: '食物', population: '人口', economy: '经济', energy: '能源' }
    return (point as any)[enMap[key]] ?? (point as any)[zhMap[key]] ?? 0
  }

  const getInitialValues = () => {
    if (data.length === 0) {
      return { food: 100, population: 100, economy: 100, energy: 100 }
    }
    return {
      food: getValue(data[0], 'food'),
      population: getValue(data[0], 'population'),
      economy: getValue(data[0], 'economy'),
      energy: getValue(data[0], 'energy')
    }
  }

  const initialValues = getInitialValues()

  const percentageData = data.map(point => ({
    month: point.month,
    食物: parseFloat(String(calculatePercentageChange(getValue(point, 'food'), initialValues.food))),
    人口: parseFloat(String(calculatePercentageChange(getValue(point, 'population'), initialValues.population))),
    经济: parseFloat(String(calculatePercentageChange(getValue(point, 'economy'), initialValues.economy))),
    能源: parseFloat(String(calculatePercentageChange(getValue(point, 'energy'), initialValues.energy)))
  }))

  const chartData = [
    { month: '初始', 食物: 0, 人口: 0, 经济: 0, 能源: 0 },
    ...percentageData
  ]

  return (
    <div className="nation-stats-chart">
      <h3>{nationName} - 资源变化趋势</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid stroke="#2E8B57" strokeDasharray="3 3" />
          <XAxis 
            dataKey="month" 
            stroke="#666"
            interval={0}
            label={{ value: '月份', position: 'insideBottom', offset: -5 }}
          />
          <YAxis 
            stroke="#666"
            domain={[-15, 15]}
            label={{ value: '变化百分比(%)', angle: -90, position: 'insideLeft' }}
          />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: '#1a1a1a',
              border: '1px solid #2E8B57',
              borderRadius: '4px'
            }}
            formatter={(value: number) => `${value}%`}
          />
          <Legend />
          <Line 
            type="monotone" 
            dataKey="食物" 
            stroke="#FF6B6B" 
            strokeWidth={2}
            dot={{ r: 4 }}
            activeDot={{ r: 6 }}
          />
          <Line 
            type="monotone" 
            dataKey="人口" 
            stroke="#4ECDC4" 
            strokeWidth={2}
            dot={{ r: 4 }}
            activeDot={{ r: 6 }}
          />
          <Line 
            type="monotone" 
            dataKey="经济" 
            stroke="#45B7D1" 
            strokeWidth={2}
            dot={{ r: 4 }}
            activeDot={{ r: 6 }}
          />
          <Line 
            type="monotone" 
            dataKey="能源" 
            stroke="#FFA07A" 
            strokeWidth={2}
            dot={{ r: 4 }}
            activeDot={{ r: 6 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

export default NationStatsChart
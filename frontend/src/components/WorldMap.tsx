import React, { useEffect, useState, useMemo } from 'react'
import { MapContainer, GeoJSON } from 'react-leaflet'
import './WorldMap.css'

interface Nation {
  id: string
  name: string
  color: string
  population: number
  territory: number
  resources: {
    food: number
    energy: number
    economy: number
  }
  attributes: {
    happiness: number
    cohesion: number
    military: number
    prestige: number
  }
}

interface WorldMapProps {
  nations: Record<string, Nation>
  onNationSelect: (nationId: string) => void
  selectedNation: string | null
}

const WorldMap: React.FC<WorldMapProps> = ({ nations, onNationSelect, selectedNation }) => {
  const [geoJsonData, setGeoJsonData] = useState<any>(null)
  const [showMenu, setShowMenu] = useState(false)
  const [menuPosition, setMenuPosition] = useState({ x: 0, y: 0 })
  const [clickedNation, setClickedNation] = useState<string | null>(null)
  const [showNationInfo, setShowNationInfo] = useState(false)

  const noiseCache = useMemo(() => new Map<string, number>(), [])
  const permutation = useMemo(() => {
    const p = new Array(512)
    const perm = new Array(256)
    for (let i = 0; i < 256; i++) {
      perm[i] = Math.floor(Math.random() * 256)
    }
    for (let i = 0; i < 512; i++) {
      p[i] = perm[i & 255]
    }
    return p
  }, [])

  const noise2D = (x: number, y: number, scale: number = 1): number => {
    const cacheKey = `${x.toFixed(2)}-${y.toFixed(2)}-${scale.toFixed(2)}`
    if (noiseCache.has(cacheKey)) {
      return noiseCache.get(cacheKey)!
    }

    const scaledX = x * scale
    const scaledY = y * scale
    
    const i = Math.floor(scaledX)
    const j = Math.floor(scaledY)
    
    const fade = (t: number) => t * t * t * (t * (t * 6 - 15) + 10)
    const lerp = (a: number, b: number, t: number) => a + t * (b - a)
    const grad = (hash: number, x: number, y: number) => {
      const h = hash & 3
      const u = h < 2 ? x : y
      const v = h < 2 ? y : x
      return ((h & 1) ? -u : u) + ((h & 2) ? -v : v)
    }
    
    const X = i & 255
    const Y = j & 255
    
    const n00 = grad(permutation[X + permutation[Y]], scaledX - i, scaledY - j)
    const n01 = grad(permutation[X + permutation[Y + 1]], scaledX - i, scaledY - (j + 1))
    const n10 = grad(permutation[X + 1 + permutation[Y]], scaledX - (i + 1), scaledY - j)
    const n11 = grad(permutation[X + 1 + permutation[Y + 1]], scaledX - (i + 1), scaledY - (j + 1))
    
    const u = fade(scaledX - i)
    const v = fade(scaledY - j)
    
    const result = lerp(lerp(n00, n10, u), lerp(n01, n11, u), v)
    
    noiseCache.set(cacheKey, result)
    return result
  }

  const fractalNoise = (x: number, y: number, octaves: number = 4, persistence: number = 0.5): number => {
    let total = 0
    let frequency = 1
    let amplitude = 1
    let maxValue = 0
    
    for (let i = 0; i < octaves; i++) {
      total += noise2D(x * frequency, y * frequency, frequency) * amplitude
      maxValue += amplitude
      amplitude *= persistence
      frequency *= 2
    }
    
    return total / maxValue
  }

  const getElevation = (lat: number, lng: number): number => {
    const baseElevation = Math.max(0, (lat - 20) / 50)
    const mountainNoise = fractalNoise(lng, lat, 6, 0.5) * 0.3
    const detailNoise = fractalNoise(lng * 2, lat * 2, 4, 0.6) * 0.15
    const microNoise = fractalNoise(lng * 4, lat * 4, 3, 0.7) * 0.05
    
    let elevation = baseElevation + mountainNoise + detailNoise + microNoise
    elevation = Math.max(0, Math.min(1, elevation))
    
    return elevation
  }

  const hslToHex = (h: number, s: number, l: number): string => {
    s /= 100
    l /= 100
    const a = s * Math.min(l, 1 - l)
    const f = (n: number) => {
      const k = (n + h / 30) % 12
      const color = l - a * Math.max(Math.min(k - 3, 9 - k, 1), -1)
      return Math.round(255 * color).toString(16).padStart(2, '0')
    }
    return `#${f(0)}${f(8)}${f(4)}`
  }

  const blendColors = (color1: string, color2: string, factor: number): string => {
    const hex = (c: string) => parseInt(c.slice(1), 16)
    const r1 = (hex(color1) >> 16) & 255
    const g1 = (hex(color1) >> 8) & 255
    const b1 = hex(color1) & 255
    
    const r2 = (hex(color2) >> 16) & 255
    const g2 = (hex(color2) >> 8) & 255
    const b2 = hex(color2) & 255
    
    const r = Math.round(r1 + (r2 - r1) * factor)
    const g = Math.round(g1 + (g2 - g1) * factor)
    const b = Math.round(b1 + (b2 - b1) * factor)
    
    return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`
  }

  const getTerrainColor = (lat: number, lng: number): string => {
    const elevation = getElevation(lat, lng)
    const noise = fractalNoise(lng * 3, lat * 3, 3, 0.6)
    const detailNoise = fractalNoise(lng * 8, lat * 8, 2, 0.8)
    
    const latFactor = (lat + 90) / 180
    
    let baseHue, baseSaturation, baseLightness
    
    if (elevation < 0.1) {
      baseHue = 220 + noise * 20
      baseSaturation = 90 + noise * 10
      baseLightness = 50 + elevation * 100 + noise * 10
    } else if (elevation < 0.25) {
      baseHue = 120 + latFactor * 20 + noise * 30
      baseSaturation = 80 + noise * 20
      baseLightness = 50 + elevation * 50 + noise * 15
    } else if (elevation < 0.4) {
      baseHue = 60 + latFactor * 30 + noise * 25
      baseSaturation = 70 + noise * 25
      baseLightness = 60 + elevation * 40 + noise * 12
    } else if (elevation < 0.6) {
      baseHue = 30 + latFactor * 20 + noise * 20
      baseSaturation = 60 + noise * 20
      baseLightness = 50 + elevation * 30 + noise * 10
    } else if (elevation < 0.8) {
      baseHue = 20 + noise * 15
      baseSaturation = 50 + noise * 15
      baseLightness = 40 + elevation * 20 + noise * 8
    } else if (elevation < 0.9) {
      baseHue = 0 + noise * 10
      baseSaturation = 30 + noise * 10
      baseLightness = 60 + noise * 15 + detailNoise * 10
    } else {
      baseHue = 200
      baseSaturation = 10
      baseLightness = 90 + noise * 10 + detailNoise * 5
    }
    
    const temperatureEffect = Math.max(0, 1 - latFactor)
    const seasonalVariation = Math.sin(lat * 0.1 + lng * 0.05) * 5
    
    baseLightness += seasonalVariation
    baseSaturation *= (0.8 + temperatureEffect * 0.4)
    
    const microVariation = detailNoise * 8
    baseLightness += microVariation
    
    baseLightness = Math.max(10, Math.min(95, baseLightness))
    baseSaturation = Math.max(10, Math.min(90, baseSaturation))
    
    const baseColor = hslToHex(baseHue, baseSaturation, baseLightness)
    
    if (elevation > 0.85) {
      const snowColor = hslToHex(0, 0, 95 + detailNoise * 5)
      const iceColor = hslToHex(200, 20, 90 + detailNoise * 5)
      return blendColors(snowColor, iceColor, Math.abs(noise))
    }
    
    if (elevation > 0.7) {
      const rockColor1 = hslToHex(30, 15, 45 + detailNoise * 10)
      const rockColor2 = hslToHex(25, 10, 55 + detailNoise * 8)
      return blendColors(rockColor1, rockColor2, Math.abs(noise))
    }
    
    return baseColor
  }

  useEffect(() => {
    fetch('/world-map.geojson')
      .then(response => response.json())
      .then(data => setGeoJsonData(data))
      .catch(error => console.error('Error loading GeoJSON:', error))
  }, [])

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const menu = document.querySelector('.context-menu')
      if (menu && !menu.contains(event.target as Node)) {
        setShowMenu(false)
      }
    }

    if (showMenu) {
      document.addEventListener('click', handleClickOutside)
      return () => {
        document.removeEventListener('click', handleClickOutside)
      }
    }
  }, [showMenu])

  const getNationForFeature = (featureIndex: number): string => {
    const nationIds = Object.keys(nations)
    if (nationIds.length === 0) return ''
    return nationIds[featureIndex % nationIds.length]
  }

  const onEachFeature = (feature: any, layer: any) => {
    const nationId = getNationForFeature(geoJsonData.features.indexOf(feature))
    const nation = nations[nationId]

    if (nation) {
      layer.on('click', (e: any) => {
        e.originalEvent.stopPropagation()
        e.originalEvent.preventDefault()
        console.log('点击了版图:', nationId)
        setClickedNation(nationId)
        setShowMenu(true)
        setMenuPosition({ x: e.originalEvent.clientX, y: e.originalEvent.clientY })
      })
    }
  }

  const style = (feature: any) => {
    const nationId = getNationForFeature(geoJsonData.features.indexOf(feature))
    const coordinates = feature.geometry.coordinates[0]
    
    let totalLat = 0
    let totalLng = 0
    let minLat = Infinity
    let maxLat = -Infinity
    let minLng = Infinity
    let maxLng = -Infinity
    
    coordinates.forEach((coord: number[]) => {
      const lat = coord[1]
      const lng = coord[0]
      totalLat += lat
      totalLng += lng
      minLat = Math.min(minLat, lat)
      maxLat = Math.max(maxLat, lat)
      minLng = Math.min(minLng, lng)
      maxLng = Math.max(maxLng, lng)
    })
    
    const centerLat = (minLat + maxLat) / 2
    const centerLng = (minLng + maxLng) / 2
    
    const noise1 = fractalNoise(centerLng * 2, centerLat * 2, 2, 0.7)
    const noise2 = fractalNoise(centerLng * 4, centerLat * 4, 3, 0.6)
    const noise3 = fractalNoise(centerLng * 8, centerLat * 8, 4, 0.5)
    
    // compute a colour purely from terrain elevation and noise so that nations no longer
    // appear as a single flat colour. this simulates a satellite‑style look
    const terrainColor = getTerrainColor(centerLat, centerLng)
    let baseColor: string = terrainColor
    
    // if you still want a very subtle tint based on the nation's assigned colour you
    // can uncomment the following lines; by default we ignore nation.color completely
    // to satisfy the '取消单一颜色' request.
    // if (nation) {
    //   const nationColor = nation.color
    //   const blendFactor = 0.05 + elevation * 0.05 + noise1 * 0.02
    //   baseColor = blendColors(terrainColor, nationColor, blendFactor)
    // }

    
    const lightnessVariation = (noise2 + noise3) * 10
    const saturationVariation = noise1 * 15
    
    const hexMatch = baseColor.match(/^#?([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})$/i)
    if (hexMatch) {
      const r = parseInt(hexMatch[1], 16)
      const g = parseInt(hexMatch[2], 16)
      const b = parseInt(hexMatch[3], 16)
      
      const hsl = rgbToHsl(r, g, b)
      hsl.l = Math.max(0, Math.min(100, hsl.l + lightnessVariation))
      hsl.s = Math.max(0, Math.min(100, hsl.s + saturationVariation))
      
      baseColor = hslToHex(hsl.h, hsl.s, hsl.l)
    }
    
    return {
      fillColor: baseColor,
      weight: selectedNation === nationId ? 3 : 1.5,
      opacity: 1,
      dashArray: selectedNation === nationId ? '' : '2,2',
      color: selectedNation === nationId ? '#ffffff' : 'rgba(0,0,0,0.3)',
      fillOpacity: selectedNation === nationId ? 0.9 : 0.8
    }
  }

  const rgbToHsl = (r: number, g: number, b: number): { h: number, s: number, l: number } => {
    r /= 255
    g /= 255
    b /= 255
    
    const max = Math.max(r, g, b)
    const min = Math.min(r, g, b)
    let h = 0
    let s = 0
    const l = (max + min) / 2
    
    if (max !== min) {
      const d = max - min
      s = l > 0.5 ? d / (2 - max - min) : d / (max + min)
      
      switch (max) {
        case r:
          h = ((g - b) / d + (g < b ? 6 : 0)) / 6
          break
        case g:
          h = ((b - r) / d + 2) / 6
          break
        case b:
          h = ((r - g) / d + 4) / 6
          break
      }
    }
    
    return { h: h * 360, s: s * 100, l: l * 100 }
  }

  const handleMenuAction = (action: string) => {
    if (clickedNation) {
      onNationSelect(clickedNation)
      if (action === 'view') {
        setShowNationInfo(true)
        setShowMenu(false)
      } else if (action === 'chat') {
        console.log('与国家对话:', clickedNation)
        setShowMenu(false)
      }
    }
  }

  return (
    <>
      <div className="world-map-container">
        <MapContainer
          center={[60, 50]}
          zoom={3}
          style={{ height: '100%', width: '100%' }}
          zoomControl={false}
        >
          {geoJsonData && (
            <GeoJSON
              key={selectedNation}
              data={geoJsonData}
              style={style}
              onEachFeature={onEachFeature}
            />
          )}
        </MapContainer>
      </div>

      {showMenu && (
        <div
          className="context-menu"
          style={{ left: menuPosition.x, top: menuPosition.y }}
        >
          <button onClick={() => handleMenuAction('view')}>查看</button>
          <button onClick={() => handleMenuAction('chat')}>对话</button>
        </div>
      )}

      {showNationInfo && clickedNation && nations[clickedNation] && (
        <div className="modal-overlay" onClick={() => setShowNationInfo(false)}>
          <div className="nation-info-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{nations[clickedNation].name}</h2>
              <button className="close-button" onClick={() => setShowNationInfo(false)}>×</button>
            </div>
            <div className="modal-body">
              <div className="info-section">
                <h3>基本信息</h3>
                <div className="info-grid">
                  <div className="info-item">
                    <span className="label">人口:</span>
                    <span className="value">{nations[clickedNation].population.toLocaleString()}</span>
                  </div>
                  <div className="info-item">
                    <span className="label">领土:</span>
                    <span className="value">{nations[clickedNation].territory}%</span>
                  </div>
                </div>
              </div>
              
              <div className="info-section">
                <h3>资源</h3>
                <div className="info-grid">
                  <div className="info-item">
                    <span className="label">🍖 食物:</span>
                    <span className="value">{nations[clickedNation].resources.food}</span>
                  </div>
                  <div className="info-item">
                    <span className="label">⚡ 能源:</span>
                    <span className="value">{nations[clickedNation].resources.energy}</span>
                  </div>
                  <div className="info-item">
                    <span className="label">💰 经济:</span>
                    <span className="value">{nations[clickedNation].resources.economy}</span>
                  </div>
                </div>
              </div>
              
              <div className="info-section">
                <h3>属性</h3>
                <div className="info-grid">
                  <div className="info-item">
                    <span className="label">😊 幸福感:</span>
                    <span className="value">{nations[clickedNation].attributes.happiness}</span>
                  </div>
                  <div className="info-item">
                    <span className="label">🤝 凝聚力:</span>
                    <span className="value">{nations[clickedNation].attributes.cohesion}</span>
                  </div>
                  <div className="info-item">
                    <span className="label">⚔️ 军事:</span>
                    <span className="value">{nations[clickedNation].attributes.military}</span>
                  </div>
                  <div className="info-item">
                    <span className="label">🏆 声望:</span>
                    <span className="value">{nations[clickedNation].attributes.prestige}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  )
}

export default WorldMap

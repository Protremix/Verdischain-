import { useEffect, useRef, useState } from 'react'

export function useAnimatedCounter(target: number, duration: number = 2000, start: boolean = true) {
  const [value, setValue] = useState(0)
  const frameRef = useRef<number>(0)

  useEffect(() => {
    if (!start) return

    let startTime: number | null = null
    const animate = (timestamp: number) => {
      if (startTime === null) startTime = timestamp
      const progress = Math.min((timestamp - startTime) / duration, 1)
      // ease-out-cubic
      const eased = 1 - Math.pow(1 - progress, 3)
      setValue(Math.floor(eased * target))
      if (progress < 1) {
        frameRef.current = requestAnimationFrame(animate)
      } else {
        setValue(target)
      }
    }

    frameRef.current = requestAnimationFrame(animate)
    return () => cancelAnimationFrame(frameRef.current)
  }, [target, duration, start])

  return value
}

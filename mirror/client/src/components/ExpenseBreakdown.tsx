import { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';

interface ExpenseData {
  category: string;
  amount: number;
  count: number;
}

interface ExpenseBreakdownProps {
  expenses: ExpenseData[];
  onCategoryClick?: (expense: ExpenseData) => void;
}

export default function ExpenseBreakdown({ expenses, onCategoryClick }: ExpenseBreakdownProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;
    
    const resizeObserver = new ResizeObserver((entries) => {
      const { width, height } = entries[0].contentRect;
      setDimensions({ width, height });
    });
    
    resizeObserver.observe(containerRef.current);
    return () => resizeObserver.disconnect();
  }, []);

  useEffect(() => {
    if (!svgRef.current || !dimensions.width || !dimensions.height || expenses.length === 0) return;

    const margin = { top: 20, right: 30, bottom: 60, left: 80 };
    const width = dimensions.width - margin.left - margin.right;
    const height = dimensions.height - margin.top - margin.bottom;

    d3.select(svgRef.current).selectAll('*').remove();

    const svg = d3.select(svgRef.current)
      .attr('width', dimensions.width)
      .attr('height', dimensions.height)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // Sort by amount descending
    const sortedData = [...expenses].sort((a, b) => Math.abs(b.amount) - Math.abs(a.amount));

    // Create scales
    const xScale = d3.scaleLinear()
      .domain([0, d3.max(sortedData, d => Math.abs(d.amount)) || 0])
      .range([0, width]);

    const yScale = d3.scaleBand()
      .domain(sortedData.map(d => d.category))
      .range([0, height])
      .padding(0.2);

    // Color scale
    const colorScale = d3.scaleOrdinal()
      .domain(sortedData.map(d => d.category))
      .range([
        'hsl(202 100% 64%)', // DexaFit blue
        'hsl(202 100% 54%)',
        'hsl(202 80% 44%)',
        'hsl(202 60% 34%)',
        'hsl(0 0% 60%)',
        'hsl(0 0% 50%)',
        'hsl(0 0% 40%)',
      ]);

    // Add bars
    svg.selectAll('.bar')
      .data(sortedData)
      .enter()
      .append('rect')
      .attr('class', 'bar')
      .attr('x', 0)
      .attr('y', d => yScale(d.category) || 0)
      .attr('width', d => xScale(Math.abs(d.amount)))
      .attr('height', yScale.bandwidth())
      .attr('fill', d => colorScale(d.category) as string)
      .attr('rx', 4)
      .style('cursor', 'pointer')
      .on('click', function(event, d) {
        console.log('Category clicked:', d);
        if (onCategoryClick) {
          onCategoryClick(d);
        }
      })
      .append('title')
      .text(d => `${d.category}\n$${Math.abs(d.amount).toFixed(2)}\n${d.count} transactions`);

    // Add value labels
    svg.selectAll('.label')
      .data(sortedData)
      .enter()
      .append('text')
      .attr('class', 'label')
      .attr('x', d => xScale(Math.abs(d.amount)) + 5)
      .attr('y', d => (yScale(d.category) || 0) + yScale.bandwidth() / 2)
      .attr('dy', '0.35em')
      .text(d => `$${Math.abs(d.amount).toFixed(0)}`)
      .style('font-size', '12px')
      .style('fill', 'hsl(0 0% 45%)');

    // Add Y axis
    svg.append('g')
      .call(d3.axisLeft(yScale))
      .style('color', 'hsl(0 0% 45%)');

    // Add X axis
    svg.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(xScale).tickFormat(d => `$${d}`))
      .style('color', 'hsl(0 0% 45%)');

  }, [expenses, dimensions, onCategoryClick]);

  return (
    <div ref={containerRef} className="w-full h-full">
      <svg ref={svgRef} className="w-full h-full" />
    </div>
  );
}

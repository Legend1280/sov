import { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';

interface Transaction {
  date: string;
  amount: number;
  description: string;
}

interface CashFlowTimelineProps {
  transactions: Transaction[];
  onTransactionClick?: (transaction: any) => void;
}

export default function CashFlowTimeline({ transactions, onTransactionClick }: CashFlowTimelineProps) {
  const svgRef = useRef<SVGSVGElement>(null);
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });
  const containerRef = useRef<HTMLDivElement>(null);

  // Update dimensions on resize
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
    if (!svgRef.current || !dimensions.width || !dimensions.height || transactions.length === 0) return;

    const margin = { top: 20, right: 30, bottom: 40, left: 60 };
    const width = dimensions.width - margin.left - margin.right;
    const height = dimensions.height - margin.top - margin.bottom;

    // Clear previous content
    d3.select(svgRef.current).selectAll('*').remove();

    const svg = d3.select(svgRef.current)
      .attr('width', dimensions.width)
      .attr('height', dimensions.height)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // Parse dates and calculate running balance
    const data = transactions
      .map(t => ({
        date: new Date(t.date),
        amount: t.amount,
        description: t.description
      }))
      .sort((a, b) => a.date.getTime() - b.date.getTime());

    let runningBalance = 0;
    const balanceData = data.map(d => {
      runningBalance += d.amount;
      return { ...d, balance: runningBalance };
    });

    // Create scales
    const xScale = d3.scaleTime()
      .domain(d3.extent(balanceData, d => d.date) as [Date, Date])
      .range([0, width]);

    const yScale = d3.scaleLinear()
      .domain([
        Math.min(0, d3.min(balanceData, d => d.balance) || 0),
        Math.max(0, d3.max(balanceData, d => d.balance) || 0)
      ])
      .nice()
      .range([height, 0]);

    // Add axes
    svg.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(xScale).ticks(6))
      .style('color', 'hsl(0 0% 45%)');

    svg.append('g')
      .call(d3.axisLeft(yScale).tickFormat(d => `$${d}`))
      .style('color', 'hsl(0 0% 45%)');

    // Add zero line
    svg.append('line')
      .attr('x1', 0)
      .attr('x2', width)
      .attr('y1', yScale(0))
      .attr('y2', yScale(0))
      .attr('stroke', 'hsl(0 0% 70%)')
      .attr('stroke-width', 1)
      .attr('stroke-dasharray', '4 4');

    // Create line generator
    const line = d3.line<typeof balanceData[0]>()
      .x(d => xScale(d.date))
      .y(d => yScale(d.balance))
      .curve(d3.curveMonotoneX);

    // Add the line path
    svg.append('path')
      .datum(balanceData)
      .attr('fill', 'none')
      .attr('stroke', 'hsl(202 100% 64%)') // DexaFit blue
      .attr('stroke-width', 2.5)
      .attr('d', line);

    // Add dots
    svg.selectAll('.dot')
      .data(balanceData)
      .enter()
      .append('circle')
      .attr('class', 'dot')
      .attr('cx', d => xScale(d.date))
      .attr('cy', d => yScale(d.balance))
      .attr('r', 4)
      .attr('fill', d => d.amount >= 0 ? 'hsl(142 76% 36%)' : 'hsl(0 84% 60%)')
      .attr('stroke', 'white')
      .attr('stroke-width', 2)
      .style('cursor', 'pointer')
      .on('click', function(event, d) {
        console.log('Transaction clicked:', d);
        if (onTransactionClick) {
          onTransactionClick(d);
        }
      })
      .append('title')
      .text(d => `${d.date.toLocaleDateString()}\n${d.description}\n$${d.amount.toFixed(2)}\nBalance: $${d.balance.toFixed(2)}`);

  }, [transactions, dimensions, onTransactionClick]);

  return (
    <div ref={containerRef} className="w-full h-full">
      <svg ref={svgRef} className="w-full h-full" />
    </div>
  );
}

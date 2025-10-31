/**
 * EventBus - Central event communication system for Mirror components
 * 
 * Enables inter-component communication without tight coupling.
 * Components can emit events and subscribe to events from other components.
 * 
 * Example:
 *   eventBus.emit('objectSelected', { id: '123', type: 'Transaction' });
 *   eventBus.on('objectSelected', (data) => console.log(data));
 */

type EventHandler = (data: any) => void;
type EventMap = Map<string, Set<EventHandler>>;

export class EventBus {
  private events: EventMap = new Map();
  private debug: boolean = false;

  constructor(debug: boolean = false) {
    this.debug = debug;
  }

  /**
   * Emit an event to all subscribers
   */
  emit(event: string, data?: any): void {
    if (this.debug) {
      console.log(`[EventBus] Emit: ${event}`, data);
    }

    const handlers = this.events.get(event);
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(data);
        } catch (error) {
          console.error(`[EventBus] Error in handler for "${event}":`, error);
        }
      });
    }
  }

  /**
   * Subscribe to an event
   */
  on(event: string, handler: EventHandler): void {
    if (!this.events.has(event)) {
      this.events.set(event, new Set());
    }
    this.events.get(event)!.add(handler);

    if (this.debug) {
      console.log(`[EventBus] Subscribed to: ${event}`);
    }
  }

  /**
   * Unsubscribe from an event
   */
  off(event: string, handler: EventHandler): void {
    const handlers = this.events.get(event);
    if (handlers) {
      handlers.delete(handler);
      if (handlers.size === 0) {
        this.events.delete(event);
      }
    }

    if (this.debug) {
      console.log(`[EventBus] Unsubscribed from: ${event}`);
    }
  }

  /**
   * Subscribe to an event once (auto-unsubscribe after first call)
   */
  once(event: string, handler: EventHandler): void {
    const onceHandler = (data: any) => {
      handler(data);
      this.off(event, onceHandler);
    };
    this.on(event, onceHandler);
  }

  /**
   * Clear all subscribers for an event
   */
  clear(event?: string): void {
    if (event) {
      this.events.delete(event);
    } else {
      this.events.clear();
    }

    if (this.debug) {
      console.log(`[EventBus] Cleared: ${event || 'all events'}`);
    }
  }

  /**
   * Get all registered event names
   */
  getEvents(): string[] {
    return Array.from(this.events.keys());
  }

  /**
   * Get subscriber count for an event
   */
  getSubscriberCount(event: string): number {
    return this.events.get(event)?.size || 0;
  }
}

// Export singleton instance
export const eventBus = new EventBus(process.env.NODE_ENV === 'development');
export default eventBus;

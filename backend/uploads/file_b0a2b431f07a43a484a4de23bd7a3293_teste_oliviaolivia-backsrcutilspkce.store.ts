export class PkceStore {
  private static map = new Map<string, string>();

  static set(state: string, verifier: string) {
    this.map.set(state, verifier);
  }

  static get(state: string): string | undefined {
    return this.map.get(state);
  }

  static delete(state: string) {
    this.map.delete(state);
  }
}

// src/utils/experimentParser.js  
class ExperimentParser {
    static parseStorage(storagePath) {
      return {
        id: path.basename(storagePath), 
        meta: this._parseMeta(storagePath),
        personas: this._parsePersonas(storagePath),
        environment: this._parseEnvironment(storagePath),
        movement: this._parseMovement(storagePath)
      }
    }
   
    static _parseMeta(storagePath) {
      const metaFile = fs.readFileSync( 
        path.join(storagePath,  'reverie/meta.json') 
      )
      return JSON.parse(metaFile) 
    }
   
    static _parsePersonas(storagePath) {
      const personasDir = path.join(storagePath,  'personas')
      return fs.readdirSync(personasDir).map(persona  => ({
        name: persona,
        memory: this._parsePersonaMemory(path.join(personasDir,  persona))
      }))
    }
   
    static _parsePersonaMemory(personaPath) {
      const memoryPath = path.join(personaPath,  'bootstrap_memory')
      return {
        associative: this._loadMemoryFile(memoryPath, 'associative_memory'),
        spatial: this._loadMemoryFile(memoryPath, 'spatial_memory.json'), 
        scratch: this._loadMemoryFile(memoryPath, 'scratch.json') 
      }
    }
   
    static _loadMemoryFile(basePath, fileName) {
      try {
        return JSON.parse(fs.readFileSync(path.join(basePath,  fileName)))
      } catch (error) {
        return null 
      }
    }
  }
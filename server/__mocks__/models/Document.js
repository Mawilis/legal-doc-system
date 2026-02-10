/* Simple mock for Document model */
module.exports = class Document {
    constructor(data) {
        Object.assign(this, data);
        this._id = data._id || 'mock_document_id';
    }
    
    save() {
        return Promise.resolve(this);
    }
    
    toObject() {
        return { ...this };
    }
    
    lean() {
        return this;
    }
    
    static findOne(query) {
        return Promise.resolve(null);
    }
    
    static find(query) {
        return Promise.resolve([]);
    }
    
    static countDocuments(query) {
        return Promise.resolve(0);
    }
    
    static updateOne(query, update) {
        return Promise.resolve({ modifiedCount: 1 });
    }
    
    static deleteOne() {
        return Promise.resolve({ deletedCount: 1 });
    }
};

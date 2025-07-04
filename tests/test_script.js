// Test JavaScript file for debugging VeriDoc rendering
console.log('Hello from test script!');

function testFunction() {
    const message = 'This is a test function';
    console.log(message);
    return message;
}

// Arrow function example
const arrowFunction = (param) => {
    return param * 2;
};

// Class example
class TestClass {
    constructor(name) {
        this.name = name;
    }
    
    greet() {
        return `Hello, ${this.name}!`;
    }
}

// Some complex JavaScript features
const asyncFunction = async () => {
    try {
        const result = await fetch('/api/health');
        return result.json();
    } catch (error) {
        console.error('Error:', error);
        throw error;
    }
};

// Object destructuring
const { name, age } = { name: 'John', age: 30 };

// Array methods
const numbers = [1, 2, 3, 4, 5];
const doubled = numbers.map(n => n * 2);
const filtered = numbers.filter(n => n > 3);

// Template literals
const template = `
    Name: ${name}
    Age: ${age}
    Doubled: ${doubled}
`;

export { testFunction, TestClass, asyncFunction };
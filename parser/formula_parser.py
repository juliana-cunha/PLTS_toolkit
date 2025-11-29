"""
Formula Parser Module.

This module handles the tokenization, parsing, and evaluation of logical formulas
in a Paraconsistent Modal Logic context (Twist Structures).

Definitions & Abbreviations:
- &  : Weak Meet (Conjunction) [sqcap]
- |  : Weak Join (Disjunction) [sqcup]
- => : Residuated Implication 
- -> : Material Implication (~A | B)
- <-> : Material Equivalence
- [] : Box
- <> : Diamond (Weighted)
- 1/TOP : Top (True)
- 0/BOT : Bottom (False)
"""

from abc import ABC, abstractmethod
from typing import Optional, Set, Any, Tuple
from ast import literal_eval

# ==========================================
#                 LEXER
# ==========================================

class Lexer:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.current_char: Optional[str] = self.text[0] if self.text else None

    def advance(self) -> None:
        self.pos += 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None

    def skip_whitespace(self) -> None:
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def get_identifier(self) -> str:
        result = ''
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()
        return result

    def get_next_token(self) -> Tuple[str, Optional[str]]:
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            
            # Modal Box [a]
            if self.current_char == '[':
                self.advance()
                if self.current_char == ']':
                    raise ValueError("Box operator '[]' requires an action identifier (e.g., [a]).")
                action = self.get_identifier()
                if not action:
                    raise ValueError("Invalid or missing action identifier inside Box operator.")
                if self.current_char == ']':
                    self.advance()
                    return ('BOX', action)
                raise ValueError("Expected ']' after action")

            # Modal Diamond <a>
            if self.current_char == '<':
                self.advance()
                
                # Check for Material IFF <->
                if self.current_char == '-':
                    self.advance()
                    if self.current_char == '>':
                        self.advance()
                        return ('MAT_IFF', '<->')
                    raise ValueError("Expected '>' after '<-'")

                # Modal Diamond <> check
                if self.current_char == '>':
                    raise ValueError("Diamond operator '<>' requires an action identifier (e.g., <a>).")

                action = self.get_identifier()
                if not action:
                     raise ValueError("Invalid or missing action identifier inside Diamond operator.")

                if self.current_char == '>':
                    self.advance()
                    return ('DIAMOND', action)
                raise ValueError("Expected '>' after action")
            
            # Residuated Implication =>
            if self.current_char == '=':
                self.advance()
                if self.current_char == '>':
                    self.advance()
                    return ('IMPLIES', '=>')
                raise ValueError(f"Unexpected character '='. Did you mean '=>'?")

            # Atoms (and Top)
            if self.current_char.isalnum():
                val = self.get_identifier()
                if val == '1' or val.upper() == 'TOP':
                    return ('ATOM', 'TOP')
                if val == '0' or val.upper() == 'BOT':
                    return ('ATOM', 'BOT')
                return ('ATOM', val)
            
            if self.current_char == '1': 
                self.advance()
                return ('ATOM', 'TOP')
            if self.current_char == '0':
                self.advance()
                return ('ATOM', 'BOT')

            # Connectives
            char_map = {
                '~': ('NOT', '~'),
                '&': ('AND', '&'), 
                '|': ('OR', '|'),  
                '(': ('LPAREN', '('),
                ')': ('RPAREN', ')')
            }

            if self.current_char in char_map:
                token = char_map[self.current_char]
                self.advance()
                return token
            
            # Material Implication ->
            if self.current_char == '-':
                self.advance()
                if self.current_char == '>':
                    self.advance()
                    return ('MAT_IMPLIES', '->')
                raise ValueError("Expected '>' after '-'")
            
            raise ValueError(f"Unknown character: {self.current_char}")
        
        return ('EOF', None)


# ==========================================
#               AST NODES
# ==========================================

class ASTNode(ABC):
    @abstractmethod
    def evaluate(self, model: Any, world: Any, twist: Any) -> Tuple[str, str]:
        pass

    @abstractmethod
    def get_atoms(self) -> Set[str]:
        pass


class Atom(ASTNode):
    def __init__(self, name: str):
        self.name = name

    def get_atoms(self) -> Set[str]:
        if self.name in ['TOP', 'BOT', '1', '0']:
            return set()
        return {self.name}

    def evaluate(self, model: Any, world: Any, twist: Any) -> Tuple[str, str]:
        if self.name == 'BOT' or self.name == '0':
            return (twist.residuated_lattice.bottom, twist.residuated_lattice.top)
        
        if self.name == 'TOP' or self.name == '1':
            return (twist.residuated_lattice.top, twist.residuated_lattice.bottom)
            
        if self.name in world.assignments:
            val_str = world.assignments[self.name]
            try:
                if val_str.startswith('('): return literal_eval(val_str)
                return (val_str, val_str)
            except:
                return (val_str, val_str)
        raise ValueError(f"Atom '{self.name}' not found in world.")


class Not(ASTNode):
    def __init__(self, child: ASTNode):
        self.child = child
    def get_atoms(self) -> Set[str]: return self.child.get_atoms()
    def evaluate(self, model: Any, world: Any, twist: Any) -> Tuple[str, str]:
        return twist.negation(self.child.evaluate(model, world, twist))


class And(ASTNode): 
    def __init__(self, left: ASTNode, right: ASTNode):
        self.left, self.right = left, right
    def get_atoms(self) -> Set[str]: return self.left.get_atoms().union(self.right.get_atoms())
    def evaluate(self, model: Any, world: Any, twist: Any) -> Tuple[str, str]:
        return twist.weak_meet(self.left.evaluate(model, world, twist), self.right.evaluate(model, world, twist))


class Or(ASTNode):
    def __init__(self, left: ASTNode, right: ASTNode):
        self.left, self.right = left, right
    def get_atoms(self) -> Set[str]: return self.left.get_atoms().union(self.right.get_atoms())
    def evaluate(self, model: Any, world: Any, twist: Any) -> Tuple[str, str]:
        return twist.weak_join(self.left.evaluate(model, world, twist), self.right.evaluate(model, world, twist))


class MaterialImplies(ASTNode):
    def __init__(self, left: ASTNode, right: ASTNode):
        self.left, self.right = left, right
    def get_atoms(self) -> Set[str]: return self.left.get_atoms().union(self.right.get_atoms())
    def evaluate(self, model: Any, world: Any, twist: Any) -> Tuple[str, str]:
        val_l = self.left.evaluate(model, world, twist)
        not_l = twist.negation(val_l)
        val_r = self.right.evaluate(model, world, twist)
        return twist.weak_join(not_l, val_r)


class MaterialIff(ASTNode):
    def __init__(self, left: ASTNode, right: ASTNode):
        self.left, self.right = left, right
    def get_atoms(self) -> Set[str]: return self.left.get_atoms().union(self.right.get_atoms())
    def evaluate(self, model: Any, world: Any, twist: Any) -> Tuple[str, str]:
        val_l = self.left.evaluate(model, world, twist)
        val_r = self.right.evaluate(model, world, twist)
        
        not_l = twist.negation(val_l)
        not_r = twist.negation(val_r)
        
        imp_lr = twist.weak_join(not_l, val_r)
        imp_rl = twist.weak_join(not_r, val_l)
        
        return twist.weak_meet(imp_lr, imp_rl)


class Implies(ASTNode):
    def __init__(self, left: ASTNode, right: ASTNode):
        self.left, self.right = left, right
    def get_atoms(self) -> Set[str]: return self.left.get_atoms().union(self.right.get_atoms())
    def evaluate(self, model: Any, world: Any, twist: Any) -> Tuple[str, str]:
        return twist.implication(self.left.evaluate(model, world, twist), self.right.evaluate(model, world, twist))


class Iff(ASTNode):
    def __init__(self, left: ASTNode, right: ASTNode):
        self.left, self.right = left, right
    def get_atoms(self) -> Set[str]: return self.left.get_atoms().union(self.right.get_atoms())
    def evaluate(self, model: Any, world: Any, twist: Any) -> Tuple[str, str]:
        v1 = self.left.evaluate(model, world, twist)
        v2 = self.right.evaluate(model, world, twist)
        return twist.weak_meet(twist.implication(v1, v2), twist.implication(v2, v1))


class Diamond(ASTNode):
    """
    Modal Diamond: <a>phi
    """
    def __init__(self, child: ASTNode, action: str):
        self.child, self.action = child, action

    def get_atoms(self) -> Set[str]: return self.child.get_atoms()

    def evaluate(self, model: Any, world: Any, twist: Any) -> Tuple[str, str]:
        if self.action not in model.actions:
            raise ValueError(f"Action '{self.action}' is not defined in Model '{model.name_model}'.")
        
        targets_map = model.accessibility_relations.get(self.action, {}).get(world, {})
        results = []
        for target, rel_weight in targets_map.items():
            val_succ = self.child.evaluate(model, target, twist)
            residue_val = twist.residue_meet(rel_weight, val_succ)
            results.append(residue_val)

        return twist.weak_join_set(results)


class Box(ASTNode):
    """
    Modal Box: [action]A
    Derived from Diamond: ~<action>~A
    """
    def __init__(self, child: ASTNode, action: str):
        self.child, self.action = child, action

    def get_atoms(self) -> Set[str]: return self.child.get_atoms()

    def evaluate(self, model: Any, world: Any, twist: Any) -> Tuple[str, str]:
        not_phi = Not(self.child)
        diamond = Diamond(not_phi, self.action)
        return twist.negation(diamond.evaluate(model, world, twist))


# ==========================================
#                 PARSER
# ==========================================

class FormulaParser:
    def __init__(self, text: str):
        self.lexer = Lexer(text)
        self.current_token = self.lexer.get_next_token()

    def eat(self, token_type: str) -> None:
        if self.current_token[0] == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            raise ValueError(f"Expected {token_type}, got {self.current_token[0]}")

    def parse(self) -> ASTNode:
        res = self.iff()
        if self.current_token[0] != 'EOF': raise ValueError("Unexpected end chars")
        return res

    def iff(self) -> ASTNode:
        node = self.implies()
        while self.current_token[0] in ('IFF', 'MAT_IFF'):
            token = self.current_token[0]
            self.eat(token)
            right = self.implies()
            if token == 'IFF':
                node = Iff(node, right)
            else:
                node = MaterialIff(node, right)
        return node

    def implies(self) -> ASTNode:
        node = self.expr_sum()
        while self.current_token[0] in ('IMPLIES', 'MAT_IMPLIES'):
            token = self.current_token[0]
            self.eat(token)
            right = self.expr_sum()
            if token == 'IMPLIES':
                node = Implies(node, right)
            else:
                node = MaterialImplies(node, right)
        return node

    def expr_sum(self) -> ASTNode:
        # Handle OR
        node = self.expr_prod()
        while self.current_token[0] == 'OR':
            self.eat('OR')
            node = Or(node, self.expr_prod())
        return node

    def expr_prod(self) -> ASTNode: 
        # Handle AND
        node = self.unary()
        while self.current_token[0] == 'AND':
            self.eat('AND')
            node = And(node, self.unary())
        return node

    def unary(self) -> ASTNode:
        token = self.current_token[0]
        val = self.current_token[1]

        if token == 'NOT':
            self.eat('NOT')
            return Not(self.unary())
        elif token == 'BOX':
            self.eat('BOX')
            return Box(self.unary(), val)
        elif token == 'DIAMOND':
            self.eat('DIAMOND')
            return Diamond(self.unary(), val)
        elif token == 'LPAREN':
            self.eat('LPAREN')
            node = self.iff()
            self.eat('RPAREN')
            return node
        elif token == 'ATOM':
            self.eat('ATOM')
            return Atom(val)
        else:
            raise ValueError(f"Unexpected token: {token}")
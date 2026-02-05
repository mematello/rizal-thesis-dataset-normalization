
import csv
import re
import os

INPUT_CANDIDATES = 'phase_d5_candidates.csv'
OUTPUT_PROPOSAL = 'phase_d6_proposal.md'

# Internal Lists for Heuristic Sorting
# These help us confidently suggest "A" for clear native words.
KNOWN_NATIVE_ROOTS = {
    'akin', 'amin', 'atin', 'ako', 'ikaw', 'siya', 'kami', 'tayo', 'kayo', 'sila',
    'ko', 'mo', 'niya', 'namin', 'natin', 'ninyo', 'nila',
    'kain', 'kilos', 'kita', 'kuha', 'kulang', 'kulay', 'kumbaba', 'kun', 'kung',
    'kupas', 'kusang', 'kuta', 'kutis',
    'baka', 'bakit', 'balibaliko', 'balik', 'balikat', 'balitang', 'banal', 'bangkay', 'bata', 'bayan',
    'bigat', 'bigay', 'bigla', 'bilang', 'bili', 'binata', 'bintana', 'bituin', 'bukas',
    'buhok', 'bulaklak', 'bulag', 'bulong', 'bundok', 'buntong', 
    'kaawa', 'kabila', 'kagat', 'kahoy', 'kailan', 'kalabaw', 'kalakal', 'kalag', 'kalam', 
    'kalap', 'kalas', 'kalat', 'kalay', 'kalik', 'kaluluwa', 'kamay', 'kami', 'kanan', 
    'kanino', 'kapag', 'kapal', 'kapatid', 'kapit', 'kapwa', 'kasi', 
    'katan', 'katawan', 'kati', 'katol', 'katulad', 'kaway', 'kay', 'kayo', 'kilos', 'kinain', 
    'ko', 'kulay', 'kong', 'kubo', 'kuha', 'kulay', 'kumbaba', 
    'kun', 'kung', 'kupas', 'kusang', 'kuta', 'kutis',
    'lakas', 'lakad', 'laking', 'lakip', 'lamang', 'langit', 'lapit', 'laro', 'layo', 'liban', 
    'likod', 'ligaya', 'limot', 'linis', 'loob', 'lukso', 'lupa', 'luwa',
    'maka', 'magka', 'magpa', 'mahal', 'mahap', 'mahirap', 'mainit', 'malaki', 'mali', 'manok', 
    'masdan', 'matanda', 'matay', 'may', 'mga', 'mula', 'muli',
    'na', 'naka', 'nagka', 'nagpa', 'nais', 'namin', 'natin', 'ng', 'ngayon', 'ngunit', 'ni', 
    'nila', 'niya', 'niyo', 'noo',
    'pa', 'paalam', 'pagka', 'pagkaka', 'paca', 'pakay', 'pako', 'pakpak', 'pag', 'pala', 
    'panahon', 'pangalan', 'pano', 'para', 'pare', 'pasok', 'patay', 'piga', 'pili', 
    'pinto', 'po', 'pula', 'puso', 'puti',
    'saan', 'sabi', 'saka', 'sakit', 'salamat', 'sama', 'samba', 'sandal', 'sang', 'sapa', 
    'sapat', 'saya', 'sayaw', 'siga', 'sigaw', 'sila', 'silid', 'sinag', 'sino', 'siya', 
    'subok', 'sukat', 'sulat', 'sundo', 'sunod',
    'tabi', 'takot', 'taho', 'tala', 'talo', 'tama', 'tanda', 'tanong', 'tao', 'tayo', 
    'tigil', 'tibay', 'tiga', 'tila', 'tinig', 'tingin', 'tipon', 'tira', 'tiwala', 
    'totoo', 'tubig', 'tulad', 'tulog', 'tuloy', 'tulong', 'tunay', 'tuntong', 'tuwa',
    'uika', 'ulan', 'uli', 'una', 'upa', 'upo', 'usap', 'utang',
    'waka', 'wala', 'wika'
}

# Prefixes that strongly suggest native word if followed by valid root
NATIVE_PREFIXES = ('pag', 'mag', 'nag', 'ma', 'na', 'ka', 'in', 'umin', 'pina', 'sina') 

def get_modernization(token):
    """
    Propose modern form for archaic token.
    Logic:
    - c -> k
    - qu -> k
    - gui -> gi
    - Keep case
    """
    lower = token.lower()
    
    # Simple transliteration map
    # 1. qu -> k (e.g. quita -> kita, aquing -> aking)
    #    qui -> ki, que -> ke (e.g. quelan -> kailan is irregular: quelan -> kelan?)
    #    Let's handle specific patterns.
    
    repl = token
    
    # Handle 'qu'
    # 'qui' -> 'ki', 'que' -> 'ke'
    repl = re.sub(r'qui', 'ki', repl, flags=re.IGNORECASE)
    repl = re.sub(r'Qui', 'Ki', repl) 
    repl = re.sub(r'que', 'ke', repl, flags=re.IGNORECASE) # Warning: 'que' might be Spanish 'que'.
    repl = re.sub(r'Que', 'Ke', repl)
    
    # Handle 'gui'
    # 'gui' -> 'gi' (e.g. guinto -> ginto)
    # Be careful with 'guinhawa' -> 'ginhawa'
    repl = re.sub(r'gui', 'gi', repl, flags=re.IGNORECASE)
    repl = re.sub(r'Gui', 'Gi', repl)

    # Handle 'c' -> 'k'
    # Only if not 'ch'. 'ch' usually stays ch in Spanish loans, or ts in Tagalog (cotsero -> kutsero was done in titles). 
    # But here we are careful. 'ch' -> preserve for now unless known root.
    # Note: 'chinelas' -> 'tsinelas' is lexical modernization.
    # Safe rule: Replace 'c' with 'k' unless followed by 'h'.
    
    # We construct a helper to replace char by char to preserve case case-sensitively
    chars = list(repl)
    new_chars = []
    i = 0
    while i < len(chars):
        c = chars[i]
        next_c = chars[i+1] if i+1 < len(chars) else ''
        
        if c.lower() == 'c':
            if next_c.lower() == 'h':
                # Preserve 'ch'
                new_chars.append(c)
                new_chars.append(next_c)
                i += 2
                continue
            else:
                # Replace with k/K
                if c.isupper():
                    new_chars.append('K')
                else:
                    new_chars.append('k')
                i += 1
        elif c.lower() == 'q' and next_c.lower() == 'u':
             # qu -> k
             # Handle previous sub logic which might have done it?
             # Actually I did regex sub above for qu/gui.
             # So 'q' remaining here shouldn't happen if regex caught it.
             # But if I used regex on 'repl' string, it's done. 
             # Let's trust regex above for qu/gui and just do c->k here for remaining Cs.
             new_chars.append(c) # Should be k from regex? No regex didn't touch C.
             i += 1
        else:
             new_chars.append(c)
             i += 1
             
    # But wait, my regex above outputted string 'repl'.
    # I should process 'repl' for 'c' -> 'k'.
    
    final_repl = ""
    i = 0
    chars = list(repl)
    while i < len(chars):
        c = chars[i]
        next_c = chars[i+1] if i+1 < len(chars) else ''
        
        if c.lower() == 'c':
            if next_c.lower() == 'h':
                final_repl += c + next_c
                i += 2
            else:
                final_repl += 'K' if c.isupper() else 'k'
                i += 1
        else:
            final_repl += c
            i += 1
            
    return final_repl

def is_safe_root(token):
    # Check if modernizing this token creates a known native root/word.
    # Normalized modernization (lowercase)
    modern = get_modernization(token).lower()
    
    # Check exact match
    if modern in KNOWN_NATIVE_ROOTS:
        return True
        
    # Check prefix
    for p in NATIVE_PREFIXES:
        if modern.startswith(p):
            root = modern[len(p):]
            if root in KNOWN_NATIVE_ROOTS:
                return True
                
    return False

def run_triage():
    if not os.path.exists(INPUT_CANDIDATES):
        print("Candidate file not found.")
        return

    print("Analyzing candidates...")
    
    categories = {
        'A': [], # Safe (Proposal)
        'B': [], # Review
        'C': []  # Preserve
    }
    
    with open(INPUT_CANDIDATES, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            token = row['token']
            count = int(row['count'])
            # d5_suggestion = row['suggested_category']
            context = row['context_snippet']
            
            # Re-Evaluate for Phase D.6 Proposal
            # 1. Clean Preserves (Modern Tagalog in list found by freq scan)
            # If token is explicitly in whitelist keys (e.g. 'kaniyang'), preserve.
            if token.lower() in KNOWN_NATIVE_ROOTS:
                 categories['C'].append((token, count, "Already Modern", context))
                 continue
                 
            # 2. Check for Modernization
            modern = get_modernization(token)
            
            if modern.lower() == token.lower():
                # No change proposed (e.g. no c, q, gui).
                # Must be Frequency Candidate or just weird.
                # If capitalized -> Name?
                if token[0].isupper():
                    categories['C'].append((token, count, "Proper Noun / Unchanged", context))
                else:
                    # Fix structure: (token, proposed, count, context, notes)
                    categories['B'].append((token, "-", count, context, "Unchanged Token (Freq)"))
                continue
            
            # 3. Analyze Change
            if is_safe_root(token):
                # Strong signal for A
                # Filter out likely Spanish matches?
                # e.g. 'cura' -> 'kura' (is 'kura' native? accepted in Filipino, but user said 'cura' -> preserve?)
                # user said: "Spanish loanwords... -> Category C (Preserve)"
                # 'cura' is Spanish.
                # My `is_safe_root` checks `KNOWN_NATIVE_ROOTS`. 'kura' is in there? 
                # I should remove 'kura', 'kotse' from KNOWN_NATIVE_ROOTS if user wants them strict Spanish.
                # I will create a BLACKLIST for "Spanish words that become Filipino but user wants preserved as Spanish"
                # Actually user said "Spanish loanwords that are not archaic Tagalog (e.g., cura, escuela, convento)".
                # So `cura` should NOT be modernized to `kura` if original is `cura`.
                # If I remove `kura` from KNOWN_NATIVE_ROOTS, `cura` will fall to B or C.
                
                categories['A'].append((token, modern, count, context))
            else:
                # Ambiguous
                # Check Spanish markers
                if any(x in token.lower() for x in ['cion', 'ción', 'ez', 'año', 'll']):
                    categories['C'].append((token, count, "Likely Spanish", context))
                # Check Capitalization
                elif token[0].isupper():
                     categories['B'].append((token, modern, count, context, "Capitalized"))
                else:
                     categories['B'].append((token, modern, count, context, "Ambiguous"))

    # Write Proposal
    print(f"Writing {OUTPUT_PROPOSAL}...")
    with open(OUTPUT_PROPOSAL, 'w', encoding='utf-8') as f:
        f.write("# Phase D.6 Modernization Proposal\n\n")
        f.write("**Action Required**: Please review Category A and B. Confirm which tokens to approve.\n\n")
        
        f.write("## Category A: Recommended Safe Modernizations\n")
        f.write("High confidence archaic Tagalog. Will be applied if approved.\n\n")
        f.write("| Token | Replacement | Count | Context |\n|---|---|---|---|\n")
        
        # Sort A by count
        cats_a = sorted(categories['A'], key=lambda x: x[2], reverse=True)
        for tok, rep, cnt, ctx in cats_a:
             ctx_short = ctx[:40].replace('\n', ' ') + "..."
             f.write(f"| `{tok}` | `{rep}` | {cnt} | {ctx_short} |\n")
             
        f.write("\n## Category B: Candidates for Review\n")
        f.write("Ambiguous tokens. Explicit approval required to apply changes.\n\n")
        f.write("| Token | Proposed | Count | Notes | Context |\n|---|---|---|---|---|\n")
        
        cats_b = sorted(categories['B'], key=lambda x: x[2], reverse=True)
        for item in cats_b:
            # Consistent structure now: (tok, rep, cnt, ctx, note)
            tok, rep, cnt, ctx, note = item
            
            ctx_short = ctx[:40].replace('\n', ' ') + "..."
            f.write(f"| `{tok}` | `{rep}` | {cnt} | {note} | {ctx_short} |\n")
            
        f.write("\n## Category C: Preserved Tokens (Sample)\n")
        f.write("Excluded from modernization (Proper Nouns, Spanish, etc).\n\n")
        f.write("| Token | Count | Reason |\n|---|---|---|\n")
        
        cats_c = sorted(categories['C'], key=lambda x: x[1], reverse=True)[:50]
        for tok, cnt, rsn, _ in cats_c:
            f.write(f"| `{tok}` | {cnt} | {rsn} |\n")
            
    print("Done.")

if __name__ == '__main__':
    run_triage()

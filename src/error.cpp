#include "pocketpy/error.h"

namespace pkpy{

    SourceData::SourceData(const Str& source, const Str& filename, CompileMode mode) {
        int index = 0;
        // Skip utf8 BOM if there is any.
        if (strncmp(source.begin(), "\xEF\xBB\xBF", 3) == 0) index += 3;
        // Drop all '\r'
        std::stringstream ss;
        while(index < source.length()){
            if(source[index] != '\r') ss << source[index];
            index++;
        }

        this->filename = filename;
        this->source = ss.str();
        line_starts.push_back(this->source.c_str());
        this->mode = mode;
    }

    std::pair<const char*,const char*> SourceData::get_line(int lineno) const {
        if(lineno == -1) return {nullptr, nullptr};
        lineno -= 1;
        if(lineno < 0) lineno = 0;
        const char* _start = line_starts.at(lineno);
        const char* i = _start;
        while(*i != '\n' && *i != '\0') i++;
        return {_start, i};
    }

    Str SourceData::snapshot(int lineno, const char* cursor, std::string_view name){
        std::stringstream ss;
        ss << "  " << "File \"" << filename << "\", line " << lineno;
        if(!name.empty()) ss << ", in " << name;
        ss << '\n';
        std::pair<const char*,const char*> pair = get_line(lineno);
        Str line = "<?>";
        int removed_spaces = 0;
        if(pair.first && pair.second){
            line = Str(pair.first, pair.second-pair.first).lstrip();
            removed_spaces = pair.second - pair.first - line.length();
            if(line.empty()) line = "<?>";
        }
        ss << "    " << line;
        if(cursor && line != "<?>" && cursor >= pair.first && cursor <= pair.second){
            auto column = cursor - pair.first - removed_spaces;
            if(column >= 0) ss << "\n    " << std::string(column, ' ') << "^";
        }
        return ss.str();
    }

    void Exception::st_push(Str&& snapshot){
        if(stacktrace.size() >= 8) return;
        stacktrace.push(std::move(snapshot));
    }

    Str Exception::summary() const {
        stack<Str> st(stacktrace);
        std::stringstream ss;
        if(is_re) ss << "Traceback (most recent call last):\n";
        while(!st.empty()) { ss << st.top() << '\n'; st.pop(); }
        if (!msg.empty()) ss << type.sv() << ": " << msg;
        else ss << type.sv();
        return ss.str();
    }

}   // namespace pkpy